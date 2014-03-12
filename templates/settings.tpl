settings for {{ user['username'] }}

<form method="post" action="/settings/update">
  <select>
  {% for subreddit in subreddits %}
    <option value="{{ subreddit['display_name'] }}">
      /r/{{ subreddit['display_name'] }} ({{ subreddit['title'] }})
    </option>
  {% endfor %}
  </select>
</form>
