
<h2>Settings for {{ user['username'] }}</h2>

<form role="form" method="post" action="/settings/update">
  <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
  <div class="form-group input-subreddit">
    <label for="subreddit">Subreddit</label>
    <div class="input-group">
      <span class="input-group-addon">/r/</span>
      <input id="subreddit" name="subreddit" value="{{ user['subreddit'] | e }}"
          type="text" class="form-control" placeholder="CollegeBasketball"
          required/>
    </div>
    <span class="help-block">
      Your bracket will be associated with the chosen subreddit. You can change
      your subreddit association at any time.
    </span>
  </div>

  <div class="form-group input-subreddit">
    <label for="subreddit">ESPN Bracket ID</label>
    <input type="text" id="bracket_id" name="bracket_id"
        value="{{ user['bracket_id'] | e }}"
        class="form-control" placeholder="12345" required pattern="[0-9]+" />
    <span class="help-block">
      Use the "entryID" field from your bracket's URL, e.g.
      <code>http://games.espn.go.com/tournament-challenge-bracket/2014/en/entry?entryID=<b>659774</b></code>
    </span>
  </div>

  <button type="submit" class="btn btn-default">Save Settings</button>
</form>

<script>
  $(function() {
    var subreddits = {{ subreddits_autocomplete | tojson | safe }};
    $('#subreddit').autocomplete({source: subreddits});

    // Lazy programmer spotted
    $('form').on('change blur keydown mousedown', function() {
      var isSubredditValid = subreddits.some(function(subreddit) {
        return subreddit.value == $('#subreddit').val();
      }) || subreddits.length == 0;
      $('#subreddit').parent().toggleClass('has-error', !isSubredditValid);
      $('#subreddit').parent().toggleClass('has-success', isSubredditValid);
      $('#subreddit')[0].setCustomValidity(
          isSubredditValid ? '' : 'Invalid subreddit');

      var isBracketIdValid = $('#bracket_id')[0].checkValidity();
      $('#bracket_id').parent().toggleClass('has-error', !isBracketIdValid);
      $('#bracket_id').parent().toggleClass('has-success', isBracketIdValid);
    });
  });
</script>
