# Python WSGI module to enable starting the application from Apache with mod_wsgi.

import sys

sys.path.insert(0, '/srv/qxlp.net/brackets/venv/lib/python3.6/site-packages')
sys.path.insert(0, '/srv/qxlp.net/brackets')

from app import app as application

