# Things to do:
# * Set up sql tables (and record statements to apply).
#
# Note: config settings should include the following built-ins:

import sys

from flask import Flask

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

@app.errorhandler(500)
def error_500(error):
    from traceback import format_exc
    return format_exc(), 500, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    app.run()

