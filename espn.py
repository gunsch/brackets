from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import concurrent.futures
import dateutil.parser
import redis
import stats
import time

import requests
import threading

ESPN_BRACKET_URL_FORMAT = (
    'https://fantasy.espn.com/games/tournament-challenge-bracket-%d/bracket?id=%s')
ESPN_BRACKET_API_FORMAT = (
    'https://gambit-api.fantasy.espn.com/apis/v1/challenges/tournament-challenge-bracket-%d/entries/%s?platform=chui&view=chui_default')

class Espn(threading.Thread):
  def __init__(self, redis_store, users, year = 2014):
    threading.Thread.__init__(self)
    self.daemon = True
    self.__redis_store = redis_store
    self.__year = year
    self.__users = users
    self.__lastrun = None
    self.__crawl_scheduled = False

  def __timestr(self, dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S")

  def get_last_run(self):
    if self.__lastrun is None:
      last_crawl_text = self.__redis_store.get('EspnLastCrawl')
      if last_crawl_text is not None:
        self.__lastrun = dateutil.parser.parse(last_crawl_text)

    if self.__lastrun is None:
      self.__update_crawl_time()

    return self.__lastrun

  def __update_crawl_time(self):
    self.__lastrun = datetime.now()
    self.__redis_store.set('EspnLastCrawl', self.__lastrun.isoformat())

  def schedule_crawl(self):
    self.__crawl_scheduled = True

  def run(self):
    while True:
      # Check periodically if the scrape flag has been set
      time.sleep(10)
      if self.__crawl_scheduled:
        print('Running a scrape at', self.__timestr(datetime.now()))

        self.update_all()

        self.__crawl_scheduled = False
        self.__update_crawl_time()

        print('Scrape finished at', self.__timestr(self.__lastrun))

  @stats.record('espn', timing = True)
  def update_all(self):
    users = self.__users.get_all_active(year = self.__year)
    users_to_save = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      scores = executor.map(self.get_score, map(lambda user: user['bracket_id'], users))
      for (score, user) in zip(scores, users):
        if score != user['bracket_score']:
          user['bracket_score'] = score
          users_to_save.append(user)

    with self.__users.get_lock():
      for user in users_to_save:
        self.__users.save(user)

    self.__users.get_all_active(year = self.__year, refresh = True)

  @stats.record('espn', timing = True)
  def get_score(self, bracket_id):
    # TODO: this could fail at any step here.
    try:
      print('Fetching score for', bracket_id)
      page = self.__get_bracket_json(bracket_id)
      score = page.get('score', {}).get('overallScore', 0)
      return score
    except:
      # Lazy hack. Easy way to notice something is wrong though.
      stats.record_one('espn-update-failure')
      return -1

  @stats.record('espn', timing = True)
  def get_bracket_name(self, bracket_id):
    try:
      page = self.__get_bracket_json(bracket_id)
      name = page.get('name', '')
      if name:
        return name
      else:
        return '[name not found]'
    except e:
      print('lookup failed for bracket %s', bracket_id)
      print(e)
      return '[error opening bracket]'

  def get_bracket_url(self, bracket_id):
    return ESPN_BRACKET_API_FORMAT % (self.__year, bracket_id)

  def __get_bracket_json(self, bracket_id):
    response = requests.get(self.get_bracket_url(bracket_id))
    return response.json()
