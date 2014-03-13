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
          <a href="http://espn.com/{{ score['bracket_id'] | e }}">{{ score['user'] | e }}</a>
          (<a href="http://www.reddit.com/u/{{ score['user'] | e }}">reddit</a>)
        </td>
        {% if not subreddit %}
        <td>
          <a href="/r/{{ score['subreddit'] | e }}">{{ score['subreddit'] | e }}</a>
        </td>
        {% endif %}
        <td>{{ score['score'] | e }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
