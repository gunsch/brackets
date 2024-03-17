{% if subreddit %}
  {% set base_link = year|string + '/r/' + subreddit %}
  <h2>Leaderboard for <a href="http://www.reddit.com/r/{{subreddit}}">/r/{{subreddit}}</a></h2>
{% else %}
  {% set base_link = year|string + '/users' %}
  <h2>Users Leaderboard</h2>
{% endif %}

{% if pages > 1 %}
<center>
Pages:
{% for page in range(1, pages + 1) %}{% if not loop.first %}, {% endif %}
<a 
    {% if page == current_page %}style="font-weight: bold;"{% endif %}
    href="/{{ base_link }}/page/{{ page }}">{{ page }}</a>{% endfor %}
</center>
{% endif %}

<table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <!-- <th>Flair</th> -->
      <th>User</th>
      {% if not subreddit %}
      <th>Subreddit</th>
      {% endif %}
      <th>Score</th>
    </tr>
  </thead>
  <tbody class="user-table">
    {% for score in scores %}
      <tr>
        <td>{{loop.index + start}}</td>
<!--         <td>
          {% if score['flair'] %}
            <span class="flair flair-{{ score['flair'] | e }}">{{ score['flair'] | e }}</span>
          {% endif %}
        </td> -->
        <td>{{ macros.user_link(score['username'], score['new_bracket_id'], year) }}</td>
        {% if not subreddit %}
        <td>{{ macros.subreddit_link(score['subreddit'], year) }}</td>
        {% endif %}
        <td>{{ score['bracket_score'] | e }}</td>
      </tr>
    {% endfor %}
  </tbody>
</table>
