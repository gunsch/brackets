# Things to do: 
# - Save espn bracket ID setting
# - users table gets espn bracket score + last updated timestamp
# - Caching/rate-limiting decorators?
# - Caching subreddit list (settings)?
# - flash message, particularly on login/saves
# - client-side subreddit validation (catch simple mistakes)
# - handle 401 when reddit expires :( store timestamp in session maybe
# 
# Note: config settings should include the following built-ins: 

import annotations  
import os
import reddit_auth
import sys
import time
import users
  
from flask import Flask, redirect, render_template, request, session
app = Flask(__name__)

@app.route("/")
def index():
  if 'db_user' in session:
    return __render('index', user = session['db_user'])
  else:
    return __render('index', user = None)

#########################################################
## Settings handlers

@app.route('/settings')
@annotations.authenticated
def settings():
  print(session['reddit_user'])
  subreddits = reddit_auth_instance.get_subreddits(session['reddit_user']['name'])
  subreddits_autocomplete = [
    {
      'label': '/r/%s (%s)' % (subreddit['display_name'], subreddit['title']),
      'value': subreddit['display_name']
    }
    for subreddit in subreddits
  ]
  return __render('settings',
      subreddits_autocomplete = subreddits_autocomplete,
      user = session['db_user'])

@app.route('/settings/update', methods = ['POST'])
@annotations.authenticated
def update_settings():
  user = session['db_user']
  user['subreddit'] = request.form['subreddit']
  users.save(user)
  return redirect('/settings')


###########################################################
## Login/logout handlers

@app.route('/login')
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

  session['reddit_user'] = user
  session['db_user'] = users.get(user['name'])
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

def __build_database_connection(app):
  return users.Users(
      host = app.config['MYSQL_HOST'],
      username = app.config['MYSQL_USERNAME'],
      password = app.config['MYSQL_PASSWORD'],
      database = app.config['MYSQL_DATABASE'])

def __render(template_name, **kwargs):
  '''
  Renders the main page, with the content section filled in as an include.

  Arguments:
  - template_name: the name of the template to invoke. Appends a '.tpl' extension
    before loading.
  - **kwargs: anything to pass to the template.
  '''
  return render_template('page.tpl',
      content_template = template_name + '.tpl', **kwargs)

# Main methods: always invoked
__load_config(app)
reddit_auth_instance = __build_reddit_auth_instance(app)
users = __build_database_connection(app)

# Startup when invoked via "python app.py"
# mod_wsgi runs the app separately
if __name__ == "__main__":
  app.run(host = app.config['HOST'], port = app.config['PORT'])
