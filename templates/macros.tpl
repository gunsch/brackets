{% macro subreddit_link(subreddit, year) -%}
  <a href="/{{ year }}/r/{{ subreddit | e }}">{{ subreddit | e }}</a>
  (<a href="http://www.reddit.com/r/{{ subreddit | e }}">reddit</a>)
{%- endmacro %}

{% macro user_link(username, bracket_id, year) -%}
  <a
      name="{{ username | e }}"
      href="http://fantasy.espn.com/tournament-challenge-bracket/{{ year  }}/en/entry?entryID={{ bracket_id| e }}"
      >{{ username | e }}</a>
  (<a href="http://www.reddit.com/u/{{ username | e }}">reddit</a>)
{%- endmacro %}
