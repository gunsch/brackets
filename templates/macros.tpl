{% macro subreddit_link(subreddit, year) -%}
  <a href="/{{ year }}/r/{{ subreddit | e }}">{{ subreddit | e }}</a>
  (<a href="http://www.reddit.com/r/{{ subreddit | e }}">reddit</a>)
{%- endmacro %}
