settings for {{ user['username'] }}

<form method="post" action="/settings/update">
  <select name="subreddit">
  <option value="">-- None --</option>
  {% for subreddit in subreddits %}
    <option
        {% if subreddit['display_name'] == user['subreddit'] %}
        selected="selected"
        {% endif %}
        value="{{ subreddit['display_name'] }}">
      /r/{{ subreddit['display_name'] }} ({{ subreddit['title'] }})
    </option>
  {% endfor %}
  </select>

  <br/>
  <input type="submit" value="Save Settings" />

</form>

