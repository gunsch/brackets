# TODO: add config settings for disabling changing preferences.

from datetime import datetime

import annotations
import brackets
import espn
import helpers
import json
import os
import random
import reddit_auth
import stats
import string
import sys
import time

from flask import Flask, Response, flash, get_flashed_messages, redirect, render_template, request, session
from flask_mobility import Mobility
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
import flask_babel
import redis

app = Flask(__name__)
flask_babel.Babel(app)
stats.Stats(app)
Mobility(app)

helpers.load_config(app)
redis_store = RedisStore(helpers.build_strict_redis(app))
KVSessionExtension(redis_store, app)

reddit_auth_instance = helpers.build_reddit_auth_instance(app)
user_manager = helpers.build_database_connection(app)
brackets = helpers.build_brackets_manager(user_manager)
espn = helpers.start_espn_manager(app)

#########################################################
## Leaderboards

@app.route("/", defaults={'year': app.config['YEAR']})
@app.route("/<int:year>/")
def index(year):
  return __render(
      'leaderboard',
      scores = brackets.get_subreddit_scores(year),
      year = year)

@app.route('/r/<subreddit>', defaults={'year': app.config['YEAR'], 'current_page': 1})
@app.route('/r/<subreddit>/page/<int:current_page>', defaults={'year': app.config['YEAR']})
@app.route('/<int:year>/r/<subreddit>', defaults={'current_page': 1})
@app.route('/<int:year>/r/<subreddit>/page/<int:current_page>')
def subreddit_leaderboard(year, subreddit, current_page):
  return __render_users_page(
      subreddit = subreddit,
      current_page = current_page,
      users = brackets.get_user_scores(year,subreddit = subreddit),
      year = year)

@app.route('/users/', defaults={'year': app.config['YEAR'], 'current_page': 1})
@app.route('/users/page/<int:current_page>', defaults={'year': app.config['YEAR']})
@app.route('/<int:year>/users/', defaults={'current_page': 1})
@app.route('/<int:year>/users/page/<int:current_page>')
def users_leaderboard(year, current_page):
  return __render_users_page(
      current_page = current_page,
      users = brackets.get_user_scores(year),
      year = year)

def __render_users_page(current_page = 1, subreddit = None, users = [], year = 0):
  page_size = app.config['USERS_PAGE_SIZE']
  start = (current_page - 1) * page_size
  return __render('users',
      subreddit = subreddit,
      current_page = current_page,
      start = start,
      pages = (len(users) - 1) // page_size + 1,
      scores = users[start : start + page_size],
      year = year)

@app.route('/<int:year>/results')
@annotations.authenticated_admin
def render_final_results(year):
    return __render(
      'final_results',
      scores = brackets.get_subreddit_winners(year),
      year = year)

@app.route('/find_self')
@annotations.authenticated
def find_self():
  score = brackets.get_user_scores(app.config['YEAR'])
  username = session['db_user']['username']
  self_index = next((i for i, score in enumerate(score)
      if score['username'] == username))

  page_size = app.config['USERS_PAGE_SIZE']
  self_page = self_index // page_size + 1
  return redirect(
      flask.url_for('users_leaderboard',
          current_page = self_page,
          _anchor = username))

@app.route('/my_bracket')
@annotations.authenticated
def espn_bracket():
  return redirect(espn.get_bracket_url(session['db_user']['bracket_id']))

#########################################################
## Control

@app.route('/refresh_all')
@annotations.authenticated_admin
def refresh_all_espn():
  espn.schedule_crawl()
  return 'Scheduling a refresh...'

#########################################################
## Settings handlers

@app.route('/mysubreddits')
@annotations.authenticated
def mysubreddits():
  return Response(json.dumps(
      reddit_auth_instance.get_subreddits(session['reddit_user']['name'])),
      mimetype = 'text/json')

@app.route('/settings')
@annotations.enable_if(app.config['BRACKET_CHANGES_ALLOWED'])
@annotations.authenticated
def settings():
  return __render('settings', year=app.config['YEAR'])

@app.route('/settings/update', methods = ['POST'])
@annotations.enable_if(app.config['BRACKET_CHANGES_ALLOWED'])
@annotations.authenticated
def update_settings():
  user = session['db_user']

  try:
    if user['subreddit'] != request.form['subreddit']:
      stats.record_one('users.change-subreddit')

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
    if not [subreddit for subreddit in user_subreddits if user['subreddit'].strip() == subreddit['display_name']]:
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

  user_age_days = (time.time() - user['created']) // 3600 // 24;
  if user_age_days < app.config['MINIMUM_USER_AGE_DAYS']:
    flash(
        'Only accounts older than %d days may participate ' %
        (app.config['MINIMUM_USER_AGE_DAYS']), category = 'error')
    return redirect('/')

  session['reddit_user'] = user
  session['db_user'] = user_manager.get(user['name'])
  session['is_admin'] = user['name'] in ['Concision', 'navytank']

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
  return flask_babel.format_timedelta(delta, granularity = 'minute')

app.jinja_env.filters['timedelta'] = format_datetime

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
      bracket_changes_allowed = app.config['BRACKET_CHANGES_ALLOWED'],
      is_admin = 'is_admin' in session and session['is_admin'],
      content_template = template_name + '.tpl',
      last_scrape_run = espn.get_last_run(),
      messages = {
        message_type: get_flashed_messages(category_filter = [message_type])
            for message_type in ['error', 'info']
      },
      latest_year = app.config['YEAR'],
      **kwargs)

# Startup when invoked via "python app.py"
# mod_wsgi runs the app separately
if __name__ == "__main__":
  app.run(host = app.config['HOST'], port = app.config['PORT'])
