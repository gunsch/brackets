{% import 'macros.tpl' as macros %}
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <meta charset="utf-8">

  <title>NCAA Bracket Competition for reddit</title>
  <link rel="stylesheet"
      href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" />
  <link rel="stylesheet"
      href="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/themes/smoothness/jquery-ui.css" />
  <!-- <link rel="stylesheet" href="/static/flair.css" /> (CI bump 2) -->
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/jquery-ui.min.js"></script>
  <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
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

  <script>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

    ga('create', 'UA-49167209-1', 'qxlp.net');
    ga('send', 'pageview');
  </script>

</body>
</html>
