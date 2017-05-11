# Udacity: Server Configuration

## Details

- IP address: `128.199.34.206`

## Configuration

- SSH listens to port `2200`
- UFW only allows ports `2200`, `80`, and `123`
- Configured UTC as timezone and sync via `ntp`
- Key-based authentication only

## Packages installed

- `apache2`, `libapache2-mod-wsgi`, `postgresql`, `python3-pip`
- `git`, `ntp`, `finger`





## Setup app server

- [ ] install apache `apt-get install apache2`
- [ ] `apt-get install libapache2-mod-wsgi`
- [ ] configure Apache to serve apython mod_wsgi application
  - For now, add the following line at the end of the <VirtualHost *:80> block, right before the closing </VirtualHost> line: WSGIScriptAlias / /var/www/html/myapp.wsgi
  - restart Apache with the sudo apache2ctl restart command
  - test with the file given as WSGIScriptAlias: /var/www/html/myapp.wsgi, code below:
  
```
def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
```


- [ ] install python3 and pip `apt-get -qqy install python3 python3-pip`
- [ ] check outdated pip packages `pip3 list -o`

## More

- deploy app
- run app
- make sure .git folder is not available outside
- A README file is included in the GitHub repo containing the following information: IP address, URL, summary of software installed, summary of configurations made, and a list of third-party resources used to completed this project.
