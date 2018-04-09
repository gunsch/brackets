from collections import defaultdict
from operator import itemgetter
from functools import cmp_to_key

# 2015 and earlier: top ten
def _scoring_original(scores):
  best_ten_scores = sorted(scores, reverse = True)[0:10]
  return sum(best_ten_scores) / 10

# 2016 and later: top max(10, n/2)
def _scoring_2016(scores):
  users_to_count = int(max(10, len(scores) / 2))
  best_scores = sorted(scores, reverse = True)[0:users_to_count]
  return sum(best_scores) / users_to_count

class Brackets:
  def __init__(self, users):
    self.__users = users

  @classmethod
  def cmp_subreddits(cls, x, y):
    # Highest score first
    if x['score'] != y['score']:
      return 1 if y['score'] > x['score'] else -1
    # If scoring has started and is tied, subs with fewer members >
    # subs with more
    if x['score'] > 0:
      return x['users_count'] - y['users_count']
    # Otherwise, just order subs by most members
    return y['users_count'] - x['users_count']

  def get_user_scores(self, year, subreddit = None):
    all_users = self.__users.get_all_active(year = year)
    users = (all_users if subreddit is None else
        [user for user in all_users if user['subreddit'] == subreddit])
    return sorted(users, key = itemgetter('bracket_score'), reverse = True)

  def get_subreddit_scores(self, year):
    subreddit_scores = defaultdict(list)
    # List of all individual bracket scores by subreddit
    for user in self.__users.get_all_active(year = year):
      subreddit_scores[user['subreddit']].append(user['bracket_score'])

    subreddits_to_display = []
    # Aggregate
    for (subreddit_name, scores) in subreddit_scores.items():
      scoring_fn = _scoring_2016 if year >= 2016 else _scoring_original
      subreddits_to_display.append({
        'subreddit': subreddit_name,
        'users_count': len(scores),
        # Format string to go to one decimal point, back to float for sorting
        'score': float('%.1f' % (scoring_fn(scores)))
      })

    return sorted(subreddits_to_display,
                  key = cmp_to_key(Brackets.cmp_subreddits))

  def get_subreddit_winners(self, year):
    '''Returns the highest-scoring users per subreddit.

    Each entry corresponds to one user/subreddit, which includes:
    *  The user object itself
    *  A 'count' field tacked on that describes the number of users that
       participated for that subreddit.
    '''

    subreddit_winners = defaultdict(lambda: {'bracket_score': -1})
    subreddit_user_counts = defaultdict(lambda: 0)
    # List of all individual bracket scores by subreddit
    for user in self.__users.get_all_active(year = year):
      subreddit_user_counts[user['subreddit']] = (
          subreddit_user_counts[user['subreddit']] + 1)
      if (subreddit_winners[user['subreddit']]['bracket_score'] < 
          user['bracket_score']):
        subreddit_winners[user['subreddit']] = user

    for subreddit, count in subreddit_user_counts.items():
      subreddit_winners[subreddit]['count'] = count

    return sorted(
        list(subreddit_winners.values()),
        key = itemgetter('count'),
        reverse = True)
