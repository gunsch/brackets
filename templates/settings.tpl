
<!-- Common issue, unfortunately. Reddit seems to drop subreddit oauth randomly. -->
<div id="settings-load-failed" class="alert alert-danger" style="display: none;">
  Could not load subreddits. Try logging out and logging in.
</div>

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
      You must choose from subreddits you subscribe to.<br/>
      Your bracket will be associated with the chosen subreddit.<br/>
      You can change your subreddit association at any time.
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
    var subreddits = [];
    var loadingInputs = $('.btn-default,#subreddit');

    $('.btn-default').text('Loading...');
    loadingInputs.prop('disabled', true);
    $.getJSON('/mysubreddits', function(server_subreddits) {
      if (!server_subreddits) {
        $('#settings-load-failed').show();
        return;
      }

      subreddits = subreddits.concat(server_subreddits.map(function(subreddit) {
        return {
          'label': '/r/' + subreddit['display_name'] + ' (' + subreddit['title'] + ')',
          'value': subreddit['display_name']
        };
      }));

      loadingInputs.prop('disabled', false);
      $('.btn-default').text('Save Settings');
      $('#subreddit').autocomplete({source: subreddits});
    });

    var espnLinkRegex = /entryID=(\d+)/;
    $('#bracket_id').on('change paste', function(e) {
      if (e.type == 'paste') {
        try {
          var str = e.originalEvent.clipboardData.getData('text/plain');
          if (matches = str.match(espnLinkRegex)) {
            $(this).val(matches[1]);
            e.preventDefault();
            return;
          }
        } catch (e) {
          // Probably different paste API, nbd
          return;
        }
      }

      if (matches = $(this).val().match(espnLinkRegex)) {
        $(this).val(matches[1]);
      }
    });

    // Lazy programmer spotted
    $('form').on('change blur keydown mousedown', function() {
      var isSubredditValid = subreddits.some(function(subreddit) {
        return subreddit.value == $('#subreddit').val();
      });
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
