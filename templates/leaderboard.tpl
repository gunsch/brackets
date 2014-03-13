<h2>Subreddit Leaderboard</h2>

<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>Subreddit</th>
      <th>Entries</th>
      <th>Score</th>
    </tr>
  </thead>
  <tbody>
    {% for score in scores %}
      <tr>
        <td>{{loop.index}}</td>
        <td>
          {{ score['subreddit'] | e }}
          (<a href="http://www.reddit.com/r/{{ score['subreddit'] | e }}">reddit</a>)
        </td>
        <td>
          <a href="/r/{{ score['subreddit'] | e }}">{{ score['users_count'] | e }}</a>
        </td>
        <td>{{ score['score'] | e }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
