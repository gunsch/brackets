<h2>Top user by subreddit (>= 10 entries)</h2>

<table class="table table-striped">
  <thead>
    <tr>
      <th>Subreddit</th>
      <th>Entries</th>
      <th>Winner</th>
      <th>Score</th>
    </tr>
  </thead>
  <tbody class="user-table">
    {% for score in scores %}
      {% if score['count'] >= 10 %}
        <tr>
          <td>{{ macros.subreddit_link(score['subreddit'], year) }}</td>
          <td>{{ score['count'] }}</td>
          <td>{{ macros.user_link(score['username'], score['bracket_id'], year) }}</td>
          <td>{{ score['bracket_score'] | e }}</td>
        </tr>
      {% endif %}
    {% endfor %}
  </tbody>
</table>
