{% macro active_for(name) -%}
  {% if content_template == name + '.tpl' %}
    class="active"
  {% endif %}
{%- endmacro %}

{% macro active_year(nav_year) -%}
  {% if nav_year == year %}
    class="active"
  {% endif %}
{%- endmacro %}

{% set base_link = '/' + year|string %}
<nav class="navbar navbar-default" role="navigation">
  <div class="container-fluid">
    <ul class="nav navbar-nav">
      <li {{ active_for('leaderboard') }}><a href="{{ base_link }}/">Leaderboard</a></li>
      <li {{ active_for('users') }}><a href="{{ base_link }}/users">Top Users</a></li>

      {% if user %}
        {% if bracket_changes_allowed %}
          <li {{ active_for('settings') }}><a href="/settings">My Bracket</a></li>
        {% else %}
          <li><a href="/find_self">Me (leaderboards)</a></li>
          <li><a href="{{ macros.bracket_href(user['new_bracket_id'], year) }}">My Bracket</a></li>
        {% endif %}

        {% if is_admin %}
        <li class="dropdown">
          <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button"
              aria-haspopup="true" aria-expanded="false">Admin
              <span class="caret"></span></a>
          <ul class="dropdown-menu">
            <li><a href="/refresh_all">Trigger Bracket Refresh</a></li>
            <li><a href="/{{year}}/results">Results</a></li>
            <li><a href="/varz">Varz</a></li>
          </ul>
        </li>
        {% endif %}

        <li><a href="/logout">Logout</a></li>
      {% else %}
        <li><a href="/login">Login</a></li>
      {% endif %}

      <li class="dropdown" style="border-left: 1px solid #ddd;">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button"
            aria-haspopup="true" aria-expanded="false">{{year}}
            <span class="caret"></span></a>
        <ul class="dropdown-menu">
          {% for nav_year in years_rendered %}
            <li {{ active_year(nav_year) }}><a href="/{{ nav_year }}">{{ nav_year }}</a></li>
          {% endfor %}
        </ul>
      </li>
    </ul>
  </div>
</nav>
