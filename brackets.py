class Brackets:
  def __init__(self):
    pass

  def get_user_scores(self, subreddit = None):
    return [
      {'user': 'navytank', 'subreddit': 'CollegeBasketball', 'bracket_id': 25, 'score': 60.2},
      {'user': 'Concision', 'subreddit': 'CollegeBasketball', 'bracket_id': 10, 'score': 45.2},
    ]

  def get_subreddit_scores(self):
    return [
      {'subreddit': 'CollegeBasketball', 'users_count': 25, 'score': 60.2},
      {'subreddit': 'uofarizona', 'users_count': 2, 'score': 45.2},
      {'subreddit': 'CFB', 'users_count': 15, 'score': 30.2},
    ]
