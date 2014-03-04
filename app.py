# Things to do: 
# * Set up sql tables (and record statements to apply). 
# 
# Note: config settings should include the following built-ins: 
  
import sys 
import os 
  
from flask import Flask, redirect, request, session 
from requests_oauthlib import OAuth2Session 
from requests.auth import HTTPBasicAuth 
import requests
  
from random import random 
from hashlib import sha1 
  
os.environ['DEBUG'] = '1'
  
auth_url = "https://ssl.reddit.com/api/v1/authorize"
token_endpoint = "https://ssl.reddit.com/api/v1/access_token"
redirect_uri = "http://127.0.0.1:5000/login/authenticated"

  
app = Flask(__name__) 
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
  
  
@app.route("/") 
def hello(): 
    return "Hello World!"
  
@app.route("/lol") 
def name_isnt_important(): 
    return "blah: new deployment test"
  
@app.route("/login") 
def login(): 
    consumer_key = app.config['CONSUMER_KEY']
    state = sha1(str(random())).hexdigest() 
  
    reddit = OAuth2Session(consumer_key, scope=['identity'], redirect_uri = redirect_uri) 
  
    authorization_url, state = reddit.authorization_url(auth_url) 
  
    session['oauth_state'] = state 
    return redirect(authorization_url) 
  
    return "this is the login page"
  
@app.route("/logout") 
def logout(): 
    return "this is the logout page"
  
@app.route("/login/authenticated") 
def login_authenticated(): 
    consumer_key = app.config['CONSUMER_KEY']
    consumer_secret = app.config['CONSUMER_SECRET']

    code = request.args.get('code', '') 
    state = request.args.get('state', '')
    assert(session['oauth_state'] == state)

    reddit = OAuth2Session(consumer_key, state=session['oauth_state'], redirect_uri = redirect_uri) 

    token = reddit.fetch_token(
        token_endpoint,
        code = code, 
        auth = HTTPBasicAuth(consumer_key, consumer_secret)) 

    #store token
    session['oauth_token'] = token

    header = {'Authorization' : 'bearer ' + token["access_token"]}
    print header

    r = requests.get('https://oauth.reddit.com/api/v1/me', headers=header)
    resp = r.json()
    return "You are authenticated as: " + resp['name']
  
@app.errorhandler(500) 
def error_500(error): 
    from traceback import format_exc 
    return format_exc(), 500, {'Content-Type': 'text/plain'} 
  
if __name__ == "__main__": 
    app.run() 