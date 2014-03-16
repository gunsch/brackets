{% macro subreddit_link(subreddit) -%}
  <a href="/r/{{ subreddit | e }}">{{ subreddit | e }}</a>
  (<a href="http://www.reddit.com/r/{{ subreddit | e }}">reddit</a>)
{%- endmacro %}
