from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import stats
import time

import requests
import threading

ESPN_BRACKET_URL_FORMAT = (
    'http://games.espn.go.com/tournament-challenge-bracket/%d/en/entry?entryID=%d')

class Espn(threading.Thread):
  def __init__(self, users, year = 2014, scrape_frequency_minutes = 5):
    threading.Thread.__init__(self)
    self.daemon = True
    self.__year = year
    self.__users = users
    self.__scrape_frequency_minutes = scrape_frequency_minutes
    self.__lastrun = datetime.now()

  def __timestr(self, dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S")

  def get_last_run(self):
    return self.__lastrun

  def run(self):
    while True:
      print 'Running a scrape at', self.__timestr(datetime.now())
      self.update_all()

      self.__lastrun = datetime.now()

      print 'Scrape finished at', self.__timestr(self.__lastrun)
      in_an_hour = self.__lastrun + timedelta(minutes = self.__scrape_frequency_minutes)
      print 'Next scrape starts at ', self.__timestr(in_an_hour)

      time.sleep(self.__scrape_frequency_minutes * 60)

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
