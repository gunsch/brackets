import MySQLdb
import MySQLdb.cursors

class Users:
  def __init__(self,
      host = 'localhost',
      username = 'root',
      password = '',
      database = ''):
    self.__connection = MySQLdb.connect(
        host = host,
        db = database,
        user = username,
        passwd = password,
        cursorclass = MySQLdb.cursors.DictCursor)
    self.__connection.autocommit(True)

  def get(self, username):
    cursor = self.__connection.cursor()
    cursor.execute('''SELECT * FROM `users` WHERE `username` = %s''', [username])
    db_user = cursor.fetchone()
    return User(db_user) if db_user is not None else User(username)

  def save(self, user):
    try:
      cursor = self.__connection.cursor()
      cursor.execute('''
        INSERT INTO `users` (`username`, `subreddit`, `espn_bracket_id`)
            VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            `subreddit` = %s,
            `espn_bracket_id` = %s
      ''',
      [
          # Insert
          user['username'], user['subreddit'], '0',
          # Update
          user['subreddit'], '0'
      ])
      return True
    except:
      return False

class User(dict):
  def __init__(self, data = None):
    if type(data) is str or type(data) is unicode:
      self['username'] = data
      self['subreddit'] = None
      self['bracket_id'] = None
    else:
      print repr(data)
      self['username'] = data['username']
      self['subreddit'] = data['subreddit']
      self['bracket_id'] = data['espn_bracket_id']
