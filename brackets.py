from collections import defaultdict
from operator import itemgetter

class Brackets:
  def __init__(self, users):
    self.__users = users

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
      ## TODO 3 --> 10
      best_ten_scores = sorted(scores, reverse = True)[0:3]
      subreddits_to_display.append({
        'subreddit': subreddit_name,
        'users_count': len(scores),
        # Format string to go to one decimal point, back to float for sorting
        'score': float('%.1f' % (float(sum(best_ten_scores))/len(best_ten_scores)))
      })

    return sorted(subreddits_to_display, key = itemgetter('score'), reverse = True)
