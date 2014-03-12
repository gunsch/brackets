# Things to do: 
# * Set up sql tables (and record statements to apply). 
# 
# Note: config settings should include the following built-ins: 
  
import sys 
import os 
  
from flask import Flask, redirect, request, session 

import reddit_auth

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

reddit_auth_instance = reddit_auth.RedditAuth(
    host = app.config['HOST'],
    port = app.config['PORT'],
    consumer_key = app.config['CONSUMER_KEY'],
    consumer_secret = app.config['CONSUMER_SECRET'])

@app.route("/")
def hello():
    if 'user' in session:
        return 'Logged in as ' + session['user']['name']
    return "Hello World! "

@app.route("/lol")
def name_isnt_important(): 
    return "blah: new deployment test"
  
@app.route("/login")
def login():
    return reddit_auth_instance.redirect_to_authorization_url()

@app.route("/logout") 
def logout(): 
    session.clear()
    return "this is the logout page"
  
@app.route("/login/authenticated") 
def login_authenticated(): 
    user = reddit_auth_instance.validate_login(request)
    if user is None:
        return 'Login failure'
    session['user'] = user
    return redirect('/')
  
@app.errorhandler(500) 
def error_500(error): 
    from traceback import format_exc 
    return format_exc(), 500, {'Content-Type': 'text/plain'} 
  
if __name__ == "__main__": 
    app.run(host = app.config['HOST'], port = app.config['PORT'])
