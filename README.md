# Udacity: Server Configuration

## Details

- IP address: [128.199.34.206](http://128.199.34.206)
- Simple version of [bookshelf app](https://github.com/b2m9/nd004-p4) is running

## Configuration

- SSH listens to port `2200`
- UFW only allows ports `2200`, `80`, and `123`
- Configured UTC as timezone and sync via `ntp`
- Key-based authentication only

## Packages installed

- `apache2`, `libapache2-mod-wsgi`, `postgresql`
- `git`, `ntp`, `finger`

## References

- [Deploy Flask on mod_wsgi](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/)
