{% macro subreddit_link(subreddit, year) -%}
  <a href="/{{ year }}/r/{{ subreddit | e }}">{{ subreddit | e }}</a>
  (<a href="https://www.reddit.com/r/{{ subreddit | e }}">reddit</a>)
{%- endmacro %}

{% macro user_link(username, bracket_id, year) -%}
  <a
      name="{{ username | e }}"
      href="https://fantasy.espn.com/games/tournament-challenge-bracket-{{ year  }}/bracket?id={{ bracket_id | e }}"
      >{{ username | e }}</a>
  (<a href="https://www.reddit.com/u/{{ username | e }}">reddit</a>)
{%- endmacro %}
