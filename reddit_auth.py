from hashlib import sha1
from random import random
from requests_oauthlib import OAuth2Session 
from requests.auth import HTTPBasicAuth 

import flask
import requests


auth_url = "https://ssl.reddit.com/api/v1/authorize"
token_endpoint = "https://ssl.reddit.com/api/v1/access_token"

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

  def redirect_to_authorization_url(self):
    '''
    Builds the redirect URL and returns the response to send the user to it.

    Sets an oauth state token for the current session.
    '''

    state = sha1(str(random())).hexdigest() 

    reddit = OAuth2Session(
        self.consumer_key,
        scope = u'identity,mysubreddits',
        redirect_uri = self.__build_login_redirect_uri()) 

    authorization_url, state = reddit.authorization_url(
        auth_url,
        duration = 'permanent')
    flask.session['oauth_state'] = state 
    return flask.redirect(authorization_url) 

  def validate_login(self, request):
    '''
    Validates a login-handle response from reddit.

    Returns None if invalid, or the user object if valid.
    '''

    code = request.args.get('code', '') 
    state = request.args.get('state', '')
    if flask.session['oauth_state'] != state:
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
    except:
        return None

    # store token for all future requests
    flask.session['oauth_token'] = token
    return self.__make_oauth_request(
        'https://oauth.reddit.com/api/v1/me').json()

  def get_subreddits(self, username):
    subreddits_json = self.__make_oauth_request(
        'https://oauth.reddit.com/subreddits/mine/subscriber').json()

    # TODO: return meaningful error
    if 'error' in subreddits_json:
        return []

    subreddits_array = [
        {
            'title': subreddit['data']['title'],
            'display_name': subreddit['data']['display_name']
        }
        for subreddit in subreddits_json['data']['children']
    ]
    return sorted(subreddits_array, key = lambda s: s['display_name'].lower())


  def __make_oauth_request(self, url):
    return requests.get(url,
        headers = {
          'Authorization' : 'bearer ' + flask.session['oauth_token']['access_token'],
          'User-Agent': 'bracket manager, by /u/Concision and /u/navytank'
        })

  def __build_login_redirect_uri(self):
    url = 'http://' + self.host
    if self.port is not None and self.port != 80:
        url = url + ':' + str(self.port)
    return url + '/login/authenticated'
