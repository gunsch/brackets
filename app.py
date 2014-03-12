# Things to do: 
# * Set up sql tables (and record statements to apply). 
# 
# Note: config settings should include the following built-ins: 
  
import os
import reddit_auth
import sys
import time
  
from flask import Flask, redirect, request, session 
app = Flask(__name__)

@app.route("/")
def index():
  if 'user' in session:
    return 'Logged in as ' + session['user']['name']
  return "Hello World! "

###########################################################
## Login/logout handlers

@app.route("/login")
def login():
  return reddit_auth_instance.redirect_to_authorization_url()

@app.route("/login/authenticated")
def login_authenticated():
  user = reddit_auth_instance.validate_login(request)
  if user is None:
    return 'Login failure'

  user_age_days = (time.time() - user['created']) / 3600 / 24;
  if user_age_days < app.config['MINIMUM_USER_AGE_DAYS']:
    return (
        'Only accounts older than %d days may participate ' %
        (app.config['MINIMUM_USER_AGE_DAYS']))

  session['user'] = user
  return redirect('/')

@app.route("/logout")
def logout():
  session.clear()
  return redirect('/')

##########################################################
## Generic handlers

@app.errorhandler(500)
def error_500(error):
  from traceback import format_exc
  return format_exc(), 500, {'Content-Type': 'text/plain'}

##########################################################
## Helper methods
def __load_config(app):
  try:
    app.config.from_object('config.settings')
  except ImportError:
    sys.stderr.write('\n'.join([
        'Could not find config file. If this is your first time running this',
        'program, try the following:',
        '',
        '    cp config.py.EXAMPLE config.py',
        '    python app.py',
        '',
        '',
    ]))
    sys.exit(-1)

def __build_reddit_auth_instance(app):
  return reddit_auth.RedditAuth(
      host = app.config['HOST'],
      port = app.config['PORT'],
      consumer_key = app.config['CONSUMER_KEY'],
      consumer_secret = app.config['CONSUMER_SECRET'])

# Main methods: always invoked
__load_config(app)
reddit_auth_instance = __build_reddit_auth_instance(app)

# Startup when invoked via "python app.py"
# mod_wsgi runs the app separately
if __name__ == "__main__":
  app.run(host = app.config['HOST'], port = app.config['PORT'])
