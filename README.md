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
pip install -r requirements.txt

# Every time: activate the venv, then start
source venv/bin/activate
python app.py
```

## Dependencies

* MySQL (make sure `mysqld` is running)
* Redis (`redis-cli ping`, then `brew services start redis` if that fails)

