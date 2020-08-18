# `debian-version-info`

Web service for viewing Debian package info status files (e.g. `/var/lib/dpkg/status`) as HTML.

Has no dependencies, uses only the Python standard library (3.7).

## Running

```
python3 main.py
```

Overriding defaults:
```
python3 main.py --address '0.0.0.0' --port 7001 --dpkg-status-file 'status.real'
```
