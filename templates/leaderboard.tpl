<h2>NCAA Bracket Subreddit Competition for {{ year }}</h2>

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
          {{ macros.subreddit_link(score['subreddit'], year) }}
        </td>
        <td>
          <a href="/{{ year }}/r/{{ score['subreddit'] | e }}">{{ score['users_count'] | e }}</a>
        </td>
        <td>{{ score['score'] | e }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>

<small>
  {% if year >= 2016 %}
  Subreddit scores are determined by averaging the highest-scoring half of all
  entries for each subreddit (minimum of ten entries used for scoring).
  {% else %}
  Subreddit scores are determined by averaging the top ten brackets for each subreddit.
  {% endif %}
  <br>Zeroes are used if a subreddit has fewer than ten members.
</small>
