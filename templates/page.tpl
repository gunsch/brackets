{% import 'macros.tpl' as macros %}
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <meta charset="utf-8">

  <title>Brackets!</title>
  <link rel="stylesheet"
      href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" />
  <link rel="stylesheet"
      href="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/themes/smoothness/jquery-ui.css" />
  <!-- <link rel="stylesheet" href="/static/flair.css" /> -->
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/jquery-ui.min.js"></script>
</head>
<body>

  {% include 'navigation.tpl' %}

  <div class="container">
    {% include 'messages.tpl' %}

    {% include content_template %}
  
    <div>
      <small>
        Scores last updated {{ last_scrape_run | timedelta }} ago
        <br/><br/>
        Built by /u/navytank and /u/Concision. Contribute on <a href="https://github.com/gunsch/brackets">Github!</a>
      </small>
    </div>

  </div>

</body>
</html>
