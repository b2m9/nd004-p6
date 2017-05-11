from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify, g, session, abort)
from flask_bootstrap import Bootstrap
from flask_github import GitHub

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from datetime import date

from forms import UpdateTopicForm, UpdateBookForm, DeleteForm, AddBookForm
from helper import get_slug
from db_bookshelf import (
    User, Book, Topic, Author, BookAuthor, BookTopic, engine
)
from github_secrets import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

# Setup Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "6RoG8rjAiYzHa4ijDTNtiEnC2XFxEwNsmexWb7pu"
app.config["GITHUB_CLIENT_ID"] = GITHUB_CLIENT_ID
app.config["GITHUB_CLIENT_SECRET"] = GITHUB_CLIENT_SECRET
bootstrap = Bootstrap(app)
github = GitHub(app)
db_session = sessionmaker(bind=engine)()


"""" SECTION: GITHUB AUTH LOGIC """


@app.before_request
def before_request():
    """Before each request, make auth token available in `g.user`."""
    g.token = None
    g.id = None
    if "token" in session:
        g.token = session["token"]
    if "id" in session:
        g.id = session["id"]


@github.access_token_getter
def token_getter():
    """Return Github's auth token to make requests on the user's behalf."""
    if g.token is not None:
        return g.token


@app.route('/login-success')
@app.route('/login-success/')
def login_successful():
    """To actually get the Github user id, we need to make another request.
    
    This redirect is a little trick to enable `token_getter` to get the user's
    Github id. All books and topics will be bound to the Github id as a owner.
    """
    gid = github.get("user")["id"]
    user = db_session.query(User).filter_by(github_id=gid).first()

    if user is None:
        db_session.add(User(github_id=gid))
        db_session.commit()

    session["id"] = gid

    flash("Login successful.", "success")
    return redirect(url_for("overview"))


@app.route("/login")
@app.route("/login/")
def login():
    """Redirect to Github authorisation page or to route "/" if user is
    already logged in or Github's client secrets are not set.
    """
    # Check if Github client secrets are set
    if app.config["GITHUB_CLIENT_ID"] and app.config["GITHUB_CLIENT_SECRET"]:
        if session.get("token", None) is None:
            return github.authorize()
        else:
            flash("Already logged in.", "info")
            return redirect(url_for("overview"))

    else:
        flash("Auth error. Please fill in Github's client secrets.", "danger")
        return redirect(url_for("overview"))


@app.route("/logout")
@app.route("/logout/")
def logout():
    """Remove auth token and redirect to route "/". Does not test if a user
    was actually logged in.
    """
    session.pop("token", None)
    session.pop("id", None)
    flash("Logout successful.", "success")
    return redirect(url_for("overview"))


@app.route("/github-callback")
@github.authorized_handler
def authorized(oauth_token):
    """Callback handler for Github OAuth.

    Sets auth token to `session.auth_token` and redirects to route "/".
    """
    next_url = request.args.get("next") or url_for("overview")

    if oauth_token is None:
        flash("Authorization failed.", "danger")
        return redirect(next_url)

    session["token"] = oauth_token
    return redirect(url_for("login_successful"))


"""" SECTION: READ TOPICS AND BOOKS """


@app.route("/")
@app.route("/<topic_slug>")
@app.route("/<topic_slug>/")
def overview(topic_slug: str="") -> tuple:
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
                           t_slug=topic_slug, books=book_list, user=g.token)


@app.route("/<topic_slug>/<book_slug>")
@app.route("/<topic_slug>/<book_slug>/")
def detail(topic_slug: str, book_slug: str) -> tuple:
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
                           t_slug=topic_slug, b_slug=book_slug, user=g.token)


"""" SECTION: JSON ENDPOINTS """


@app.route("/JSON")
@app.route("/JSON/")
@app.route("/<topic_slug>/JSON")
@app.route("/<topic_slug>/JSON/")
def handle_json(topic_slug: str=""):
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


@app.errorhandler(401)
def error_404(e: Exception) -> tuple:
    """Render `templates/401.html` if 401 error."""
    return render_template("401.html", exception=e, user=g.token), 401


@app.errorhandler(403)
def error_404(e: Exception) -> tuple:
    """Render `templates/403.html` if 401 error."""
    return render_template("403.html", exception=e, user=g.token), 401


@app.errorhandler(404)
def error_404(e: Exception) -> tuple:
    """Render `templates/404.html` if 404 error."""
    return render_template("404.html", exception=e, user=g.token), 404


@app.errorhandler(500)
def error_500(e: Exception) -> tuple:
    """Render `templates/500.html` if 500 error."""
    return render_template('500.html', exception=e, user=g.token), 500


"""" SECTION: HELPER FUNCTIONS TO RE-USE QUERIES """


def get_topic_by_slug(slug: str) -> Topic:
    """Return one `Topic` by given `slug`."""
    return db_session.query(Topic).filter_by(slug=slug).one()


def get_book_by_slug(slug: str) -> Book:
    """Return one `Book` by given `slug`."""
    return db_session.query(Book).filter_by(slug=slug).one()


def get_authors_by_book_id(book_id: int) -> list:
    """Return list of `Author.name` for given `book_id`."""
    return [a[0] for a in (
        db_session.query(Author.name)
        .join(BookAuthor, Book)
        .filter(and_(BookAuthor.book_id == book_id))
        .all()
    )]


def get_topic_by_name(name: str) -> list:
    """Return all `Topic` objects matching given `name`."""
    return db_session.query(Topic).filter_by(name=name).all()


def get_author_by_name(name: str) -> list:
    """Return all `Author` objects matching given `name`."""
    return db_session.query(Author).filter_by(name=name).all()


def create_book_slug(title: str) -> str:
    """Return unique slug for `Book`."""
    return get_slug([b.slug for b in db_session.query(Book).all()], title)


def create_topic_slug(name: str) -> str:
    """Return unique slug for `Topic`."""
    return get_slug([t.slug for t in (db_session.query(Topic).all())], name)


def delete_bookauthor_by_book_id(book_id: int) -> None:
    """Delete all references in `BookAuthor` matching given `book_id`."""
    delete_list(
        db_session.query(BookAuthor)
        .filter_by(book_id=book_id)
        .all()
    )


def delete_bookless_authors() -> None:
    """Delete all `Author` objects without references in `BookAuthor`."""
    delete_list(
        db_session.query(Author)
        .outerjoin(BookAuthor)
        .filter(BookAuthor.author_id == None)  # `is None` doesn't work
        .all()
    )


def delete_bookless_topics() -> None:
    """Delete all `Topic` objects without references in `BookTopic`."""
    delete_list(
        db_session.query(Topic)
        .outerjoin(BookTopic)
        .filter(BookTopic.topic_id == None)  # `is None` doesn't work
        .all()
    )


def delete_topicless_books() -> None:
    """Delete all `Book` objects without references in `BookTopic`."""
    delete_list(
        db_session.query(Book)
        .outerjoin(BookTopic)
        .filter(BookTopic.book_id == None)  # `is None` doesn't work
        .all()
    )


def delete_list(db_list: list) -> None:
    """Delete a list of SQLAlchemy objects.

    Necessary because `session.delete` can only delete single elements.
    """
    for l in db_list:
        db_session.delete(l)

if __name__ == '__main__':
    # Automatically reload changed Jinja templates
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host="0.0.0.0", port=5000)
