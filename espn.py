from bs4 import BeautifulSoup
import requests

ESPN_BRACKET_URL_FORMAT = (
    'http://games.espn.go.com/tournament-challenge-bracket/2014/en/entry?entryID=%d')

class Espn:
  def __init__(self, users):
    self.__users = users

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
