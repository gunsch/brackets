from flask import flash
from functools import wraps
import MySQLdb
import MySQLdb.cursors
import stats
import sys
import traceback

class Users:
  def __init__(self,
      host = 'localhost',
      username = 'root',
      password = '',
      database = ''):
    self.__host = host
    self.__username = username
    self.__password = password
    self.__database = database
    self.__reconnect()

  def __reconnect(self):
    self.__connection = MySQLdb.connect(
        host = self.__host,
        db = self.__database,
        user = self.__username,
        passwd = self.__password,
        cursorclass = MySQLdb.cursors.DictCursor)
    self.__connection.autocommit(True)

  def __reconnect_on_failure(fn):
    @wraps(fn)
    def reconnecting_fn(self, *args, **kwargs):
      try:
        return fn(self, *args, **kwargs)
      except MySQLdb.OperationalError:
        stats.record('users.mysql-failure')
        self.__reconnect()
        return fn(self, *args, **kwargs)
    return reconnecting_fn

  @stats.record('users', timing = True)
  def get(self, username):
    db_user = self.__get(username)
    return User(db_user) if db_user is not None else User(username)

  @__reconnect_on_failure
  def __get(self, username):
    cursor = self.__connection.cursor()
    cursor.execute('''SELECT * FROM `users` WHERE `username` = %s''', [username])
    item = cursor.fetchone()
    cursor.close()
    return item

  @stats.record('users', timing = True)
  @__reconnect_on_failure
  def get_all_active(self):
    cursor = self.__connection.cursor()
    cursor.execute('''SELECT * FROM `users` WHERE `espn_bracket_id` > 0''')
    data = map(User, cursor.fetchall())
    cursor.close()
    return data

  @stats.record('users', timing = True)
  @__reconnect_on_failure
  def save(self, user):
    try:
      db_user = self.__get(user['username'])
      cursor = self.__connection.cursor()
      if db_user is not None:
        cursor.execute('''
          UPDATE `users` SET
              `subreddit` = %s,
              `espn_bracket_id` = %s,
              `espn_bracket_score` = %s,
              `flair` = %s
          WHERE `username` = %s
        ''',
        [user['subreddit'], user['bracket_id'], user['bracket_score'], user['flair'], user['username']])
        return True
      else:
        cursor.execute('''
          INSERT INTO `users`
              (`username`, `subreddit`, `espn_bracket_id`, `espn_bracket_score`, `flair`)
              VALUES (%s, %s, %s, %s, %s)
        ''',
        [user['username'], user['subreddit'], user['bracket_id'], user['bracket_score'], user['flair']])
      cursor.close()

    except MySQLdb.IntegrityError, e:
      flash('Settings not saved. Your bracket ID may only be used once.',
          category = 'error');
      traceback.print_exc()
      return False

    except:
      flash('Settings not saved. Unknown error.', category = 'error');
      traceback.print_exc()
      return False

class User(dict):
  def __init__(self, data = None):
    if type(data) is str or type(data) is unicode:
      self['username'] = data
      self['subreddit'] = ''
      self['bracket_id'] = 0
      self['bracket_score'] = 0
      self['flair'] = ''
    else:
      self['username'] = data['username']
      self['subreddit'] = data['subreddit']
      self['bracket_id'] = data['espn_bracket_id']
      self['bracket_score'] = data['espn_bracket_score']
      self['flair'] = data['flair']
