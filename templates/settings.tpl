
<h2>Settings for {{ user['username'] }}</h2>

<form role="form" method="post" action="/settings/update">
  <div class="form-group input-subreddit">
    <label for="subreddit">Subreddit</label>
    <div class="input-group">
      <span class="input-group-addon">/r/</span>
      <input id="subreddit" name="subreddit" value="{{ user['subreddit'] | e }}"
          type="text" class="form-control" placeholder="CollegeBasketball" />
    </div>
    <span class="help-block">
      Your bracket will be associated with the chosen subreddit. You can change
      your subreddit association at any time.
    </span>
  </div>

  <div class="form-group input-subreddit">
    <label for="subreddit">ESPN Bracket ID</label>
    <input type="text" name="bracket_id" value="{{ user['bracket_id'] | e }}"
        class="form-control" placeholder="12345" />
    <span class="help-block">
      Some text about how to find the bracket ID. Maybe paste in the URL.
    </span>
  </div>

  <button type="submit" class="btn btn-default">Save Settings</button>
</form>

<script>
  $(function() {
    $('#subreddit').autocomplete({
      source: {{ subreddits_autocomplete | tojson | safe }}
    });
  });
</script>
