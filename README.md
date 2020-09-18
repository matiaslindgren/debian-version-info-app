# `debian-version-info`

Web service for viewing Debian package info status files (e.g. `/var/lib/dpkg/status`) as HTML.

The only dependency is Python 3.7 or later, everything is implemented using the Python standard library.

## Running

```
python3 main.py
```
Then go to <localhost:8000>.

Overriding defaults:
```
python3 main.py --address '0.0.0.0' --port 7001 --dpkg-status-file 'status.real'
```

## Deploying


### Locally 
Build `deploy.dockerfile` as a Docker image to get executable containers that bind to `0.0.0.0` at the port given by environment variable `PORT`.

### On Heroku

First create an app named `debian-version-info` (or something else) on Heroku.

Then [deploy as a container](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml):
```
heroku login
heroku git:remote -a debian-version-info
heroku stack:set container
git push heroku master
```
