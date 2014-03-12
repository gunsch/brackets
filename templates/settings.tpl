
settings for {{ user['username'] }}

<form method="post" action="/settings/update">
  /r/<input id="subreddit" name="subreddit" value="{{ user['subreddit'] | e }}" />
  <br/>
  <input type="submit" value="Save Settings" />
</form>

<script>
  $(function() {
    $('#subreddit').autocomplete({
      source: {{ subreddits_autocomplete | tojson | safe }}
    });
  });
</script>
