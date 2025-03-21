from flask import flash
from functools import wraps
from threading import Lock
import annotations
import pymysql
import pymysql.cursors
import stats
import sys
import traceback

class Users:
  def __init__(self,
      host = 'localhost',
      username = 'root',
      password = '',
      database = '',
      year = 0):
    self.__host = host
    self.__username = username
    self.__password = password
    self.__database = database
    self.__year = year
    self.__reconnect()
    self.__lock = Lock()
    # Sanity check
    if year == 0:
      raise Exception('Year may not be empty.')

  def __reconnect(self):
    self.__connection = pymysql.connect(
        host = self.__host,
        db = self.__database,
        user = self.__username,
        passwd = self.__password,
        cursorclass = pymysql.cursors.DictCursor)
    self.__connection.autocommit(True)

  def __reconnect_on_failure(fn):
    @wraps(fn)
    def reconnecting_fn(self, *args, **kwargs):
      try:
        return fn(self, *args, **kwargs)
      except (pymysql.OperationalError, pymysql.err.InterfaceError) as err:
        stats.record('users.mysql-failure')
        self.__reconnect()
        return fn(self, *args, **kwargs)
    return reconnecting_fn

  def get_lock(self):
    '''Careful. This is the raw lock.'''
    return self.__lock

  @stats.record('users', timing = True)
  def get(self, username):
    db_user = self.__get(username)
    return User(db_user) if db_user is not None else User(username, year = self.__year)

  @__reconnect_on_failure
  def __get(self, username):
    cursor = self.__connection.cursor()
    cursor.execute('''SELECT * FROM `users` WHERE `username` = %s AND `year` = %s''',
        [username, self.__year])
    item = cursor.fetchone()
    cursor.close()
    return item

  @annotations.redis_cache('all_active_users', cache_key_args = ['year'], cache_seconds = 60)
  @__reconnect_on_failure
  @stats.record('users', timing = True)
  def get_all_active(self, *args, **kwargs):
    # Kind of silly, but since the cache operates on kwargs, this is a simple
    # way to enforce that "year" isn't passed in as an arg.
    if len(args) > 0:
      raise Exception('get_all_active only takes kwargs')
    year = kwargs['year']
    if not year:
      year = self.__year
    with self.get_lock():
      cursor = self.__connection.cursor()
      cursor.execute('''SELECT * FROM `users` WHERE `year` = %s AND `espn_new_bracket_id` != ""''', [year])
      data = list(map(User, cursor.fetchall()))
      cursor.close()
    return data

  @__reconnect_on_failure
  @stats.record('users', timing = True)
  def save(self, user):
    try:
      db_user = self.__get(user['username'])
      cursor = self.__connection.cursor()
      if db_user is not None:
        cursor.execute('''
          UPDATE `users` SET
              `subreddit` = %s,
              `espn_bracket_id` = 0,
              `espn_new_bracket_id` = %s,
              `espn_bracket_score` = %s,
              `flair` = %s
          WHERE `username` = %s AND `year` = %s
        ''',
        [user['subreddit'], user['new_bracket_id'], user['bracket_score'], user['flair'], user['username'], self.__year])
      else:
        cursor.execute('''
          INSERT INTO `users`
              (`username`, `subreddit`, `espn_bracket_id`, `espn_new_bracket_id`, `espn_bracket_score`, `flair`, `year`)
              VALUES (%s, %s, 0, %s, %s, %s, %s)
        ''',
        [user['username'], user['subreddit'], user['new_bracket_id'], user['bracket_score'], user['flair'], self.__year])
      cursor.close()
      return True

    except pymysql.IntegrityError:
      flash('Settings not saved. Your bracket ID may only be used once.',
          category = 'error');
      traceback.print_exc()
      return False

    except:
      flash('Settings not saved. Unknown error.', category = 'error');
      traceback.print_exc()
      return False

class User(dict):
  def __init__(self, data = None, year = 0):
    if type(data) is str:
      self['username'] = data
      self['subreddit'] = ''
      self['new_bracket_id'] = ''
      self['bracket_score'] = 0
      self['flair'] = ''
      self['year'] = year
      # Sanity check
      if year == 0:
        raise Exception('No year specified for empty user.')
    else:
      self['username'] = data['username']
      self['subreddit'] = data['subreddit']
      self['new_bracket_id'] = data['espn_new_bracket_id']
      self['bracket_score'] = data['espn_bracket_score']
      self['flair'] = data['flair']
      self['year'] = data['year']
