{% if subreddit %}
<h2>Leaderboard for <a href="http://www.reddit.com/r/{{subreddit}}">/r/{{subreddit}}</a></h2>
{% else %}
<h2>Users Leaderboard</h2>
{% endif %}

<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>User</th>
      {% if not subreddit %}
      <th>Subreddit</th>
      {% endif %}
      <th>Score</th>
    </tr>
  </thead>
  <tbody>
    {% for score in scores %}
      <tr>
        <td>{{loop.index}}</td>
        <td>
          <a href="http://games.espn.go.com/tournament-challenge-bracket/2014/en/entry?entryID={{ score['bracket_id'] | e }}"
              >{{ score['username'] | e }}</a>
          (<a href="http://www.reddit.com/u/{{ score['username'] | e }}">reddit</a>)
        </td>
        {% if not subreddit %}
        <td>
          {{ macros.subreddit_link(score['subreddit']) }}
        </td>
        {% endif %}
        <td>{{ score['bracket_score'] | e }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
