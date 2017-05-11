# Udacity: Server Configuration

- [ ] add SSH key
- [ ] delete root user
- [ ] update all package lists `apt-get update`
- [ ] upgrade all packages `apt-get upgrade`
- [ ] remove un-used packages `apt-get autoremove`
- [ ] change the SSH port from 22 to 2200

- [ ] install apache `apt-get install apache2` ?
- [ ] install postgresql `apt-get install postgresql`
- [ ] install finger `apt-get install finger`

- [ ] configure the local timezone to UTC
- [ ] configure Apache to serve apython mod_wsgi application

- [ ] install python3 and pip `apt-get -qqy install python3 python3-pip`
- [ ] upgrade pip `pip3 install --upgrade pip`
- [ ] check outdated pip packages `pip3 list -o`

- [ ] create a new user account named grader
  - `adduser grader`
  - `finger grader`
- [ ] give grader the permission to sudo
  - create file `/etc/sudoers.d/grader`
  - `nano into it`
  - write `grader ALL=(ALL) NOPASSWD:ALL`
  - test sudo access as grader with `sudo cat /etc/passwd`
- [ ] create an SSH key pair for grader using the ssh-keygen tool
  - login as grader `ssh grader@ip -p port`
