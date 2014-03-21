from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import dateutil.parser
import redis
import stats
import time

import requests
import threading

ESPN_BRACKET_URL_FORMAT = (
    'http://games.espn.go.com/tournament-challenge-bracket/%d/en/entry?entryID=%d')

class Espn(threading.Thread):
  def __init__(self, users, year = 2014):
    threading.Thread.__init__(self)
    self.daemon = True
    self.__redis_store = redis.StrictRedis()
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
        print 'Running a scrape at', self.__timestr(datetime.now())

        self.update_all()

        self.__crawl_scheduled = False
        self.__update_crawl_time()

        print 'Scrape finished at', self.__timestr(self.__lastrun)

  @stats.record('espn', timing = True)
  def update_all(self):
    users = self.__users.get_all_active()
    users_to_save = []
    for user in users:
      score = self.get_score(user['bracket_id'])
      if score != user['bracket_score']:
        user['bracket_score'] = score
        users_to_save.append(user)
    for user in users_to_save:
      self.__users.save(user)

  @stats.record('espn', timing = True)
  def get_score(self, bracket_id):
    # TODO: this could fail at any step here.
    try:
      page = self.__get_bracket_page(bracket_id)
      score_el = page.find(class_ = 'points_CurrentSegment')
      score = score_el.get_text()
      # >1000 scores have commas
      return int(score.replace(',', ''))
    except:
      # Lazy hack. Easy way to notice something is wrong though.
      stats.record_one('espn-update-failure')
      return -1

  @stats.record('espn', timing = True)
  def get_bracket_name(self, bracket_id):
    try:
      page = self.__get_bracket_page(bracket_id)
      name_el = page.find(class_ = 'entryName')
      return name_el.get_text()
    except:
      return '[name not found]'

  def __get_bracket_page(self, bracket_id):
    request = requests.get(ESPN_BRACKET_URL_FORMAT % (self.__year, bracket_id))
    return BeautifulSoup(request.text)
