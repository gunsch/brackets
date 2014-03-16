from bs4 import BeautifulSoup
import time

import requests
import threading

ESPN_BRACKET_URL_FORMAT = (
    'http://games.espn.go.com/tournament-challenge-bracket/2014/en/entry?entryID=%d')

class Espn(threading.Thread):
  def __init__(self, users, scrape_frequency_minutes = 5):
    threading.Thread.__init__(self)
    self.daemon = True
    self.__users = users
    self.__scrape_frequency_minutes = scrape_frequency_minutes

  def __timestr(self, time_struct):
    return time.strftime("%a, %d %b %Y %H:%M:%S", time_struct)

  def run(self):
    while True:
      print 'Running a scrape at', self.__timestr(time.localtime())
      self.update_all()

      print 'Scrape finished at', self.__timestr(time.localtime())
      # Not worth figuring out how to do correctly
      in_an_hour = time.localtime(time.mktime(time.localtime()) +
          self.__scrape_frequency_minutes * 60)
      print 'Next scrape starts at ', self.__timestr(in_an_hour)
      time.sleep(self.__scrape_frequency_minutes * 60)

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

  def get_score(self, bracket_id):
    # TODO: this could fail at any step here.
    request = requests.get(ESPN_BRACKET_URL_FORMAT % bracket_id)
    page = BeautifulSoup(request.text)
    score_el = page.find(class_ = 'points_CurrentSegment')
    score = score_el.get_text()
    # >1000 scores have commas
    return int(score.replace(',', ''))
