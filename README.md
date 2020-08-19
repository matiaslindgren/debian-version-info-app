# `debian-version-info`

Web service for viewing Debian package info status files (e.g. `/var/lib/dpkg/status`) as HTML.

The only dependency is Python 3.7 or later, everything is implemented using the Python standard library.

## Running

```
python3 main.py
```
Then go to [`localhost:8000`].

Overriding defaults:
```
python3 main.py --address '0.0.0.0' --port 7001 --dpkg-status-file 'status.real'
```
