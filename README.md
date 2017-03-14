[![Build Status](https://travis-ci.org/whatever4711/PyMon.svg?branch=master)](https://travis-ci.org/whatever4711/PyMon)

[![](https://images.microbadger.com/badges/version/whatever4711/pymon:amd64-latest.svg)](https://microbadger.com/images/whatever4711/pymon:amd64-latest "Get your own version badge on microbadger.com") [![](https://images.microbadger.com/badges/image/whatever4711/pymon:amd64-latest.svg)](https://microbadger.com/images/whatever4711/pymon:amd64-latest "Get your own image badge on microbadger.com") [![](https://images.microbadger.com/badges/commit/whatever4711/pymon:amd64-latest.svg)](https://microbadger.com/images/whatever4711/pymon:amd64-latest "Get your own commit badge on microbadger.com")

[![](https://images.microbadger.com/badges/version/whatever4711/pymon:armhf-latest.svg)](https://microbadger.com/images/whatever4711/pymon:armhf-latest "Get your own version badge on microbadger.com") [![](https://images.microbadger.com/badges/image/whatever4711/pymon:armhf-latest.svg)](https://microbadger.com/images/whatever4711/pymon:armhf-latest "Get your own image badge on microbadger.com") [![](https://images.microbadger.com/badges/commit/whatever4711/pymon:armhf-latest.svg)](https://microbadger.com/images/whatever4711/pymon:armhf-latest "Get your own commit badge on microbadger.com")

[![](https://images.microbadger.com/badges/version/whatever4711/pymon:aarch64-latest.svg)](https://microbadger.com/images/whatever4711/pymon:aarch64-latest "Get your own version badge on microbadger.com") [![](https://images.microbadger.com/badges/image/whatever4711/pymon:aarch64-latest.svg)](https://microbadger.com/images/whatever4711/pymon:aarch64-latest "Get your own image badge on microbadger.com") [![](https://images.microbadger.com/badges/commit/whatever4711/pymon:aarch64-latest.svg)](https://microbadger.com/images/whatever4711/pymon:aarch64-latest "Get your own commit badge on microbadger.com")

# PyMon

This is a django project, which collects data from [monit](https://mmonit.com/monit) instances on one or multiple servers, stores them and visualizes them using [bootstrap](http://getbootstrap.com/) and the javascript library [dygraphs](http://dygraphs.com/).

There is a very similar app for the server monitoring tool [supervisor](https://github.com/Supervisor/supervisor) called [djangovisor](https://github.com/nleng/djangovisor).


### Features
- Collects and parses monit xml data from one or multiple servers.
- Stores the data for a given time period.
- Displays it in pretty graphs.
- Start/stop/restart buttons for processes.
- Status tables and graphs are refreshing automatically via ajax.
- Processes are automatically removed when they stop sending data (removed from monitrc). Servers can be deleted manually.

### Installation

Just install it via pip:
```
pip install django-monit-collector
```
Or clone the repository if you want to modify the code:
```
git clone https://github.com/nleng/django-monit-collector
```

Add 'monitcollector' to your installed apps in settings.py:
```
INSTALLED_APPS = [
    'monitcollector',
    # ...
]
```
If you want to you can change the default values in your settings.py:
```
# should be the same as set in the monitrc file e.g. "set daemon 60"
MONIT_UPDATE_PERIOD = 60
# maximum days to store data, only correct, if MONIT_UPDATE_PERIOD is set correctly
MAXIMUM_STORE_DAYS = 7
```
Include monitcollector in your url.py:
```
url(r'^monitcollector/', include('monitcollector.urls')),
```
Create/sync the database and create a superuser (you need to login to access the monit-collector dashboard):
```
python manage.py syncdb
```
Collect static files:
```
python manage.py collectstatic
```
With correct webserver configurating the app should then be available at http://mydomain.com/monitcollector/.

In your monitrc file add this line to send data to the collector.
```
set mmonit http://mydomain.com/monitcollector/collector
```
If you want to enable the start/stop buttons (optional), the monit http daemon must be available, in monitrc (you can also)
```
set httpd port 2812
  allow myuser:mypassword
```
If you don't want to allow access from everywhere add "allow ip.address..." with the ip address of the server, where monitcollector is installed.
The user and password have to be set in the .env file (Copy the existing env to .env and change your settings locally):
```
ENABLE_BUTTONS = True
MONIT_USER = youruser
MONIT_PASSWORD = yourpassword
MONIT_PORT = 2812
```
You don't have to specify the port if you use the default port 2812. Also, the port must not me blocked by the firewall, e.g.
```
ufw allow 2812
```

You can also monitor this app with monit itself. Not using the privided script lead to error in my case.
```
check process monitcollector with pidfile /path/to/pid/gunicorn.pid
  start program = "/project/path/gunicorn.sh start"
  stop program = "/project/path/gunicorn.sh stop"
  if failed host 127.0.0.1 port 8011 protocol http then restart
  if 5 restarts within 5 cycles then alert
```
Then you should have the same port and pid path in your gunicorn.conf
```
bind = '127.0.0.1:8011'
...
pidfile = '/path/to/pid/gunicorn.pid'
```

### License
BSD License.
