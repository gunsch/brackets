class Brackets:
  def __init__(self, users):
    self.__users = users

  def get_user_scores(self, subreddit = None):
    all_users = self.__users.get_all_active()
    if subreddit is None:
      return all_users
    return filter(lambda user: user['subreddit'] == subreddit, all_users)

  def get_subreddit_scores(self):
    return [
      {'subreddit': 'CollegeBasketball', 'users_count': 25, 'score': 60.2},
      {'subreddit': 'uofarizona', 'users_count': 2, 'score': 45.2},
      {'subreddit': 'CFB', 'users_count': 15, 'score': 30.2},
    ]
