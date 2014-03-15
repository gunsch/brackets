from bs4 import BeautifulSoup
import requests

ESPN_BRACKET_URL_FORMAT = (
    'http://games.espn.go.com/tournament-challenge-bracket/2013/en/entry?entryID=%d')

class Espn:
  def __init__(self, users):
    self.__users = users

  def update_all(self):
    pass

  def get_score(self, bracket_id):
    # TODO: this could fail at any step here.
    request = requests.get(ESPN_BRACKET_URL_FORMAT % bracket_id)
    page = BeautifulSoup(request.text)
    score_el = page.find(class_ = 'points_CurrentSegment')
    score = score_el.get_text()
    # >1000 scores have commas
    return int(score.replace(',', ''))
