# Caching todo:
# 1) Leaderboard pages need to be memoized. Not at the route level (caching
#    logged-in UI), but at a level that either includes or takes into account
#    the scraping time
#
# - pip requirements file, setup script (run all sql)

from datetime import datetime

import annotations
import brackets
import espn
import json
import os
import random
import reddit_auth
import stats
import string
import sys
import time
import users

from flask import Flask, Response, flash, get_flashed_messages, redirect, render_template, request, session
import flask.ext.babel
app = Flask(__name__)
babel = flask.ext.babel.Babel(app)
stats.Stats(app)

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

@app.route('/mysubreddits')
@annotations.authenticated
def mysubreddits():
  return Response(json.dumps(
      reddit_auth_instance.get_subreddits(session['reddit_user']['name'])),
      mimetype = 'text/json')

@app.route('/settings')
@annotations.authenticated
def settings():
  return __render('settings')

@app.route('/settings/update', methods = ['POST'])
@annotations.authenticated
def update_settings():
  user = session['db_user']

  try:
    user['subreddit'] = request.form['subreddit']
    user['bracket_id'] = int(request.form['bracket_id'])

    bracket_name = espn.get_bracket_name(user['bracket_id'])
    if (app.config.get('ENFORCE_BRACKET_NAMES_MATCH', False) and
        user['username'].strip() != bracket_name.strip()):
      flash('ESPN bracket name must be the same as your reddit username: '
          'found "%s", expected "%s"' % (bracket_name, user['username']),
          category = 'error')
      return redirect('/settings')

    user_subreddits = reddit_auth_instance.get_subreddits(
        session['reddit_user']['name'])
    if not filter(
        lambda subreddit: user['subreddit'].strip() == subreddit['display_name'],
        user_subreddits):
      flash('Subreddit "%s" not found. Ensure you are subscribed to the '
          'subreddit and that it is typed correctly.' % user['subreddit'],
          category = 'error')
      return redirect('/settings')

    if user_manager.save(user):
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
  session['db_user'] = user_manager.get(user['name'])

  # Sort of a hack: flair is only accessible via a single extra reddit request.
  # We can't list all flairs for the subreddit. So instead, we do it once on
  # login. This means we should save it right away.
  #if 'flair' in user:
  #  session['db_user']['flair'] = user['flair']
  #  user_manager.save(session['db_user'])

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
  stats.record_one('500')
  from traceback import format_exc
  return format_exc(), 500, {'Content-Type': 'text/plain'}

@app.before_request
def record_request():
  stats.record_one('request')

# CSRF handling, mostly taken from:
# http://flask.pocoo.org/snippets/3/
# How the hell does Flask not include CSRF support
@app.before_request
def csrf_protect():
  if request.method == 'POST':
    token = session.get('_csrf_token', None)
    if not token or token != request.form.get('_csrf_token'):
      stats.record_one('csrf_failure')
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

def __build_brackets_manager(user_manager):
  return brackets.Brackets(user_manager)

def __start_espn_manager(app):
  espn_manager = espn.Espn(
      # Start separate connection for ESPN, since it's on background thread
      __build_database_connection(app),
      year = app.config['YEAR'],
      scrape_frequency_minutes = app.config['SCRAPE_FREQUENCY_MINUTES'])
  espn_manager.start()
  return espn_manager

@stats.record('app')
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
      year = app.config['YEAR'],
      **kwargs)

# Main methods: always invoked
__load_config(app)
reddit_auth_instance = __build_reddit_auth_instance(app)
user_manager = __build_database_connection(app)
brackets = __build_brackets_manager(user_manager)
espn = __start_espn_manager(app)

# Startup when invoked via "python app.py"
# mod_wsgi runs the app separately
if __name__ == "__main__":
  app.run(host = app.config['HOST'], port = app.config['PORT'])
