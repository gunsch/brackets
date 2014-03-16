# Things to do:
# - Caching/rate-limiting decorators?
# - Caching subreddit list (settings)? -- probably slowest part of the site
# - note: caching will have to happen at a function level, with the ability to
#   get timestamps out. imagine homepage table with "last updated".
# - server-side subreddit validation (what does this look like?)
# - pip requirements file, setup script (run all sql)

from datetime import datetime

import annotations
import brackets
import espn
import os
import random
import reddit_auth
import string
import sys
import time
import users

from flask import Flask, flash, get_flashed_messages, redirect, render_template, request, session
import flask.ext.babel
app = Flask(__name__)
babel = flask.ext.babel.Babel(app)

#########################################################
## Leaderboards

@app.route("/")
def index():
  return __render('leaderboard', scores = brackets.get_subreddit_scores())

@app.route("/r/<subreddit>")
def subreddit_leaderboard(subreddit):
  return __render('users',
      subreddit = subreddit,
      scores = brackets.get_user_scores(subreddit))

@app.route("/users")
def users_leaderboard():
  return __render('users',
      scores = brackets.get_user_scores())

#########################################################
## Settings handlers

@app.route('/settings')
@annotations.authenticated
def settings():
  subreddits = reddit_auth_instance.get_subreddits(session['reddit_user']['name'])
  subreddits_autocomplete = [
    {
      'label': '/r/%s (%s)' % (subreddit['display_name'], subreddit['title']),
      'value': subreddit['display_name']
    }
    for subreddit in subreddits
  ]
  return __render('settings',
      subreddits_autocomplete = subreddits_autocomplete)

@app.route('/settings/update', methods = ['POST'])
@annotations.authenticated
def update_settings():
  user = session['db_user']

  try:
    user['subreddit'] = request.form['subreddit']
    user['bracket_id'] = int(request.form['bracket_id'])
    if users.save(user):
      flash('Settings saved.', category = 'info');

  except ValueError:
    flash('Settings not saved: bracket ID must be an integer (see the '
        'entryID=XXXXX value in your ESPN bracket URL).', category = 'error')

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
    flash('Login error.', category = 'error')
    return redirect('/')

  user_age_days = (time.time() - user['created']) / 3600 / 24;
  if user_age_days < app.config['MINIMUM_USER_AGE_DAYS']:
    flash(
        'Only accounts older than %d days may participate ' %
        (app.config['MINIMUM_USER_AGE_DAYS']), category = 'error')
    return redirect('/')

  session['reddit_user'] = user
  session['db_user'] = users.get(user['name'])

  # If no subreddit is set yet, go directly to settings page
  if not session['db_user']['subreddit']:
    return redirect('/settings')

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

# CSRF handling, mostly taken from:
# http://flask.pocoo.org/snippets/3/
# How the hell does Flask not include CSRF support
@app.before_request
def csrf_protect():
  if request.method == 'POST':
    token = session.get('_csrf_token', None)
    if not token or token != request.form.get('_csrf_token'):
      flask.abort(403)

def generate_csrf_token():
  if '_csrf_token' not in session:
    session['_csrf_token'] = ''.join(
        random.choice(string.ascii_letters) for _ in range(20))
  return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# Delta formatting
def format_datetime(time):
  delta = datetime.now() - time
  return flask.ext.babel.format_timedelta(delta, granularity = 'minute')

app.jinja_env.filters['timedelta'] = format_datetime

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

def __build_brackets_manager(users):
  return brackets.Brackets(users)

def __start_espn_manager(users):
  espn_manager = espn.Espn(users,
      scrape_frequency_minutes = app.config['SCRAPE_FREQUENCY_MINUTES'])
  espn_manager.start()
  return espn_manager

def __render(template_name, **kwargs):
  '''
  Renders the main page, with the content section filled in as an include.

  Arguments:
  - template_name: the name of the template to invoke. Appends a '.tpl' extension
    before loading.
  - **kwargs: anything to pass to the template.
  '''
  return render_template('page.tpl',
      user = session['db_user'] if 'db_user' in session else None,
      content_template = template_name + '.tpl',
      last_scrape_run = espn.get_last_run(),
      messages = {
        message_type: get_flashed_messages(category_filter = [message_type])
            for message_type in ['error', 'info']
      },
      **kwargs)

# Main methods: always invoked
__load_config(app)
reddit_auth_instance = __build_reddit_auth_instance(app)
users = __build_database_connection(app)
brackets = __build_brackets_manager(users)
espn = __start_espn_manager(users)

# Startup when invoked via "python app.py"
# mod_wsgi runs the app separately
if __name__ == "__main__":
  app.run(host = app.config['HOST'], port = app.config['PORT'])
