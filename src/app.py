from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify, session, abort)
from flask_bootstrap import Bootstrap

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db_bookshelf import (
    User, Book, Topic, Author, BookAuthor, BookTopic, engine
)

# Setup Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "6RoG8rjAiYzHa4ijDTNtiEnC2XFxEwNsmexWb7pu"
bootstrap = Bootstrap(app)
db_session = sessionmaker(bind=engine)()


@app.route("/")
@app.route("/<topic_slug>")
@app.route("/<topic_slug>/")
def overview(topic_slug=""):
    """Render `templates/overview.html` for "/" and "/<topic_slug>".

    Route "/":
        Display all books ordered by `pub_date` from `bookshelf_db.Book`.

    Route "/<topic_slug>":
        Display only the books associated with the given `topic_slug`.

    Args:
        topic_slug: Unique human-friendly slug to identify topic.

    Raises:
        SQLAlchemyError: Given `topic_slug` not found in `bookshelf_db.Topic`.
            Abort with error code 404.
    """
    topic_list = db_session.query(Topic.name, Topic.slug).all()

    if len(topic_slug) == 0:
        topic_slug = "python"

    try:
        # Return 404 in case of invalid `topic_slug`
        topic = get_topic_by_slug(topic_slug).name
        book_list = (
            db_session.query(Book.title, Book.slug, Topic.slug)
            .join(BookTopic, Topic)
            .filter(and_(Topic.slug == topic_slug))
            .all()
        )
    except SQLAlchemyError as sa_err:
        return abort(404, sa_err)

    return render_template("overview.html", topics=topic_list, topic=topic,
                           t_slug=topic_slug, books=book_list)


@app.route("/<topic_slug>/<book_slug>")
@app.route("/<topic_slug>/<book_slug>/")
def detail(topic_slug="", book_slug=""):
    """Render `templates/detail.html` for "/<topic_slug>/<book_slug>".

    Route "/<topic_slug>/<book_slug>":
        Display all details associated with this book from `bookshelf_db.Book`.
        Query for associated authors from `bookshelf_db.Author`.

    Args:
        topic_slug: Unique human-friendly slug to identify topic.
        book_slug: Unique human-friendly slug to identify book.

    Raises:
        SQLAlchemyError: Given `topic_slug` or `book_slug` not found in
            `bookshelf_db.Topic` or `bookshelf_db.Book` respectively. Abort
            with error code 404.
    """
    try:
        # Return 404 in case of invalid `topic_slug` or `book_slug`
        get_topic_by_slug(topic_slug)
        book = get_book_by_slug(book_slug)
        authors = get_authors_by_book_id(book.id)
    except SQLAlchemyError as sa_err:
        return abort(404, sa_err)

    return render_template("detail.html", book=book, authors=authors,
                           t_slug=topic_slug, b_slug=book_slug)


"""" SECTION: JSON ENDPOINTS """


@app.route("/JSON")
@app.route("/JSON/")
@app.route("/<topic_slug>/JSON")
@app.route("/<topic_slug>/JSON/")
def handle_json(topic_slug=""):
    if len(topic_slug):
        try:
            # Return 404 in case of invalid `topic_slug`
            get_topic_by_slug(topic_slug)  # Necessary to throw exception
            books = (
                db_session.query(Book)
                .join(BookTopic, Topic)
                .filter(and_(Topic.slug == topic_slug))
                .all()
            )
        except SQLAlchemyError as sa_err:
            return abort(404, sa_err)
    else:
        books = db_session.query(Book).all()

    return jsonify(books=[b.serialize() for b in books])


"""" SECTION: ERROR HANDLERS """


@app.errorhandler(404)
def error_404(e):
    """Render `templates/404.html` if 404 error."""
    return render_template("404.html", exception=e), 404


"""" SECTION: HELPER FUNCTIONS TO RE-USE QUERIES """


def get_topic_by_slug(slug):
    """Return one `Topic` by given `slug`."""
    return db_session.query(Topic).filter_by(slug=slug).one()


def get_book_by_slug(slug):
    """Return one `Book` by given `slug`."""
    return db_session.query(Book).filter_by(slug=slug).one()


def get_authors_by_book_id(book_id):
    """Return list of `Author.name` for given `book_id`."""
    return [a[0] for a in (
        db_session.query(Author.name)
        .join(BookAuthor, Book)
        .filter(and_(BookAuthor.book_id == book_id))
        .all()
    )]


def get_topic_by_name(name):
    """Return all `Topic` objects matching given `name`."""
    return db_session.query(Topic).filter_by(name=name).all()


def get_author_by_name(name):
    """Return all `Author` objects matching given `name`."""
    return db_session.query(Author).filter_by(name=name).all()


if __name__ == '__main__':
    # Automatically reload changed Jinja templates
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=5000)
