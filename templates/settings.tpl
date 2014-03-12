settings for {{ user['username'] }}

<select>
{% for subreddit in subreddits %}
  <option value="{{ subreddit['display_name'] }}">
    /r/{{ subreddit['display_name'] }} ({{ subreddit['title'] }})
  </option>
{% endfor %}
</select>
