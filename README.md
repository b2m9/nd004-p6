# Udacity: Server Configuration

## Update existing packages

- [ ] update all package lists `apt-get update`
- [ ] upgrade all packages `apt-get upgrade`
- [ ] remove un-used packages `apt-get autoremove`

## Secure server

- [ ] change the SSH port from 22 to 2200
- [ ] configure UFW to only allow 2200, 80, and 123
  - `ufw status`
  - `ufw default deny incoming`
  - `ufw default allow outgoing`
  - standard ssh: `ufw allow ssh`
  - custom port: `ufw allow 2200/tcp`
  - http: `ufw allow www`
  - `ufw enable`

## User

- [ ] create a new user account named grader
  - `adduser grader`
  - `finger grader`
- [ ] give grader the permission to sudo
  - create file `/etc/sudoers.d/grader`
  - `nano into it`
  - write `grader ALL=(ALL) NOPASSWD:ALL`
  - test sudo access as grader with `sudo cat /etc/passwd`
- [ ] create an SSH key pair for grader using the ssh-keygen tool
- [ ] add SSH key
  - `mkdir .ssh` in /home/grader as grader
  - `touch .ssh/authorized_keys` and `nano` into it
  - copy paste ssh public key
  - `chmod 700 .ssh`
  - `chmod 644 .ssh/authorized_keys`
  - login as grader `ssh grader@ip -p port -i ~/.ssh/key`
- [ ] Disable password-based login
  - `nano /etc/ssh/sshd_config`
  - change to `PasswordAuthentication no`
  - restart ssh service `service ssh restart`
- [ ] delete root user

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

- [ ] install postgresql `apt-get install postgresql`
- [ ] install finger `apt-get install finger`


- [ ] configure the local timezone to UTC



- [ ] install python3 and pip `apt-get -qqy install python3 python3-pip`
- [ ] upgrade pip `pip3 install --upgrade pip`
- [ ] check outdated pip packages `pip3 list -o`
- [ ] install git

## More

- deploy app
- run app
- make sure .git folder is not available outside
- A README file is included in the GitHub repo containing the following information: IP address, URL, summary of software installed, summary of configurations made, and a list of third-party resources used to completed this project.
