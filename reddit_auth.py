from requests_oauthlib import OAuth2Session 
from requests.auth import HTTPBasicAuth 
import requests
import flask

from random import random
from hashlib import sha1

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
        scope = ['identity'],
        redirect_uri = self.__build_login_redirect_uri()) 

    authorization_url, state = reddit.authorization_url(auth_url) 

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

    #store token
    flask.session['oauth_token'] = token

    get_user_request = requests.get(
        'https://oauth.reddit.com/api/v1/me',
        headers = {'Authorization' : 'bearer ' + token['access_token']})
    return get_user_request.json()

  def __build_login_redirect_uri(self):
    url = 'http://' + self.host
    if self.port is not None:
        url = url + ':' + str(self.port)
    return url + '/login/authenticated'
