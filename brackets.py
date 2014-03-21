from collections import defaultdict
from operator import itemgetter

class Brackets:
  def __init__(self, users):
    self.__users = users

  @classmethod
  def cmp_subreddits(cls, x, y):
    # Highest score first
    if x['score'] != y['score']:
      return int(y['score'] - x['score'])
    # If scoring has started and is tied, subs with fewer members >
    # subs with more
    if x['score'] > 0:
      return x['users_count'] - y['users_count']
    # Otherwise, just order subs by most members
    return y['users_count'] - x['users_count']

  def get_user_scores(self, subreddit = None):
    all_users = self.__users.get_all_active()
    users = all_users if subreddit is None else filter(
        lambda user: user['subreddit'] == subreddit, all_users)
    return sorted(users, key = itemgetter('bracket_score'), reverse = True)

  def get_subreddit_scores(self):
    subreddit_scores = defaultdict(list)
    # List of all individual bracket scores by subreddit
    for user in self.__users.get_all_active():
      subreddit_scores[user['subreddit']].append(user['bracket_score'])

    subreddits_to_display = []
    # Aggregate
    for (subreddit_name, scores) in subreddit_scores.iteritems():
      best_ten_scores = sorted(scores, reverse = True)[0:10]
      subreddits_to_display.append({
        'subreddit': subreddit_name,
        'users_count': len(scores),
        # Format string to go to one decimal point, back to float for sorting
        'score': float('%.1f' % (float(sum(best_ten_scores)) / 10))
      })

    return sorted(subreddits_to_display, cmp = Brackets.cmp_subreddits)
