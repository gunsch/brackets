import brackets
import espn
import os
import users
import reddit_auth
import redis
import static_hack
import sys

##########################################################
## Helper methods
def load_config(app):
  try:
    app.config.from_object('config.settings')

    # Allow overriding any specific config entry with environment variable
    # named BRACKET_[CONFIG_NAME]. This does some hacky parsing to determine
    # the value type, since env vars all come in as strings.
    import config
    config_keys = list(filter(lambda x: not x.startswith('_'), dir(config.settings)))
    for key in config_keys:
      env_field_name = 'BRACKET_' + key
      if env_field_name in os.environ:
        value = os.environ[env_field_name]
        # Lazy-hack parsing
        if value == 'True':
          value = True
        elif value == 'False':
          value = False
        elif value.isnumeric():
          value = int(value)
        app.config[key] = value
        print('overriding', key, 'from environment')

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

def build_reddit_auth_instance(app):
  return reddit_auth.RedditAuth(
      login_host = app.config['LOGIN_HOST'],
      user_agent = app.config['USER_AGENT'],
      consumer_key = app.config['CONSUMER_KEY'],
      consumer_secret = app.config['CONSUMER_SECRET'])

def build_database_connection(app):
  return users.Users(
      host = app.config['MYSQL_HOST'],
      username = app.config['MYSQL_USERNAME'],
      password = app.config['MYSQL_PASSWORD'],
      database = app.config['MYSQL_DATABASE'],
      year = app.config['YEAR'])

def build_brackets_manager(user_manager):
  return brackets.Brackets(user_manager)

def start_espn_manager(app):
  espn_manager = espn.Espn(
      build_strict_redis(app),
      # Start separate connection for ESPN, since it's on background thread
      build_database_connection(app),
      year = app.config['YEAR'])
  espn_manager.start()
  return espn_manager

def build_strict_redis(app):
  return static_hack.get_redis_HACK(
      callback = lambda: redis.StrictRedis(
          host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT']))
