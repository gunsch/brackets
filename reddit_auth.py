from hashlib import sha1
from random import random
from requests_oauthlib import OAuth2Session 
from requests.auth import HTTPBasicAuth 

import annotations
import flask
import requests
import stats

auth_url = "https://www.reddit.com/api/v1/authorize"
token_endpoint = "https://www.reddit.com/api/v1/access_token"

class RedditAuth:
  def __init__(self,
      host = '127.0.0.1',
      port = 5000,
      consumer_key = None,
      consumer_secret = None):
    self.host = host
    self.port = port
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret

  @stats.record('reddit', timing = True)
  def redirect_to_authorization_url(self):
    '''
    Builds the redirect URL and returns the response to send the user to it.

    Sets an oauth state token for the current session.
    '''

    state = sha1(str(random())).hexdigest() 

    reddit = OAuth2Session(
        self.consumer_key,
        scope = u'identity,mysubreddits', #,flair',
        redirect_uri = self.__build_login_redirect_uri()) 

    authorization_url, state = reddit.authorization_url(
        auth_url,
        duration = 'permanent')
    flask.session['oauth_state'] = state 
    return flask.redirect(authorization_url) 

  @stats.record('reddit', timing = True)
  def validate_login(self, request):
    '''
    Validates a login-handle response from reddit.

    Returns None if invalid, or the user object if valid.
    '''

    code = request.args.get('code', '') 
    state = request.args.get('state', '')
    if flask.session['oauth_state'] != state:
      print 'Invalid oauth state in session'
      return None

    try:
      reddit = OAuth2Session(
          self.consumer_key,
          state = flask.session['oauth_state'],
          redirect_uri = self.__build_login_redirect_uri())

      token = reddit.fetch_token(
          token_endpoint,
          code = code,
          auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret))
    except Exception as e:
      print 'Failed to fetch token from reddit', e
      return None

    # store token for all future requests
    flask.session['oauth_token'] = token
    user = self.__make_oauth_request(
        'https://oauth.reddit.com/api/v1/me').json()
    if user is None:
      print 'Failed to make request to /api/v1/me'
      return None

    # get flair right away
    #flair_response = self.__make_oauth_post(
    #    'https://oauth.reddit.com/r/CollegeBasketball/api/flairselector',
    #    {'name': user['name']}).json()
    #if flair_response is not None and 'current' in flair_response:
    #  user['flair'] = flair_response['current']['flair_css_class']

    return user

  @annotations.session_cache('mysubreddits')
  @stats.record('reddit', timing = True)
  def get_subreddits(self, username):
    subreddits_seen = 0
    user_subreddits = []

    # Load 100 (max) subreddits at a time
    params = {'limit': 100}
    next_subreddit_start = None
    while True:
      params['count'] = len(user_subreddits)
      if next_subreddit_start is not None:
        params['after'] = next_subreddit_start

      subreddits_json = self.__make_oauth_request(
          'https://oauth.reddit.com/subreddits/mine/subscriber',
          params = params).json()

      if 'error' in subreddits_json:
        print 'Error loading subreddits:', repr(subreddits_json)
        return None

      user_subreddits.extend([
          {
              'title': subreddit['data']['title'],
              'display_name': subreddit['data']['display_name']
          }
          for subreddit in subreddits_json['data']['children']
      ])

      if subreddits_json['data']['after']:
        next_subreddit_start = subreddits_json['data']['after']
      else:
        print 'Loaded', len(user_subreddits), 'subreddits'
        break
    return sorted(user_subreddits, key = lambda s: s['display_name'].lower())

  @stats.record('reddit')
  def __make_oauth_request(self, url, params = None):
    return requests.get(url,
        params = params,
        headers = {
          'Authorization' : 'bearer ' + flask.session['oauth_token']['access_token'],
          'User-Agent': 'bracket manager, by /u/Concision and /u/navytank'
        })

  @stats.record('reddit')
  def __make_oauth_post(self, url, data):
    return requests.post(url, data = data,
        headers = {
          'Authorization' : 'bearer ' + flask.session['oauth_token']['access_token'],
          'User-Agent': 'bracket manager, by /u/Concision and /u/navytank'
        })

  def __build_login_redirect_uri(self):
    url = 'http://' + self.host
    if self.port is not None and self.port != 80:
      url = url + ':' + str(self.port)
    return url + '/login/authenticated'
