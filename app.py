# Things to do:
# * file-based configuration. Set up mysql connection.
#
# Note: config settings should include the following built-ins:
# DEBUG = True
# SECRET_KEY (?)
# SQL login info

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/lol")
def name_isnt_important():
    return "blah"

@app.errorhandler(500)
def error_500(error):
    from traceback import format_exc
    return format_exc(), 500, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    app.run()

