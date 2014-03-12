<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Brackets!</title>

  <style type="text/css">
    /* TODO move to separate file */

  </style>

  <link rel="stylesheet"
      href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" />
  <link rel="stylesheet"
      href="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/themes/smoothness/jquery-ui.css" />
  <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.4/jquery-ui.min.js"></script>
</head>
<body>

  {% include 'navigation.tpl' %}

  <div class="container">
    {% include content_template %}
  </div>

</body>
</html>
