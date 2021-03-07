brackets
========

Group competition bracket manager.

Run application either:
* Locally: `python3 app.py`
* Via Apache (WSGI), using [Flask's WSGI docs](http://flask.pocoo.org/docs/deploying/mod_wsgi/) and app.wsgi

## Setup

Run the following:

```
# One time: set up a virtualenv
python3 -m venv ./venv/
source venv/bin/activate
pip3 install -r requirements.txt

# One-time: create a database and populate the schema
mysql -u root -p <<< 'create database brackets'
cat sql/* | mysql -u root brackets

# One-time: copy the config file, modify it as needed
cp config.py.EXAMPLE config.py

# Every time: activate the venv, then start
source venv/bin/activate
python3 app.py
```

## Dependencies

* MySQL (make sure `mysqld` is running)
* Redis (`redis-cli ping`, then `brew services start redis` if that fails)

