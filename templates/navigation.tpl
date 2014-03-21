{% macro active_for(name) -%}
  {% if content_template == name + '.tpl' %}
    class="active"
  {% endif %}
{%- endmacro %}

<nav class="navbar navbar-default" role="navigation">
  <div class="container-fluid">
    <ul class="nav navbar-nav">
      <li {{ active_for('leaderboard') }}><a href="/">Leaderboard</a></li>
      <li {{ active_for('users') }}><a href="/users">Top Users</a></li>

      {% if user %}
        {% if bracket_changes_allowed %}
          <li {{ active_for('settings') }}><a href="/settings">My Bracket</a></li>
        {% else %}
          <li><a href="/find_self">Me (leaderboards)</a></li>
          <li><a href="/my_bracket">My Bracket</a></li>
        {% endif %}

        {% if is_admin %}
        <li><a href="/refresh_all">Trigger Bracket Refresh</a></li>
        <li><a href="/varz">Varz</a></li>
        {% endif %}

        <li><a href="/logout">Logout</a></li>
      {% else %}
        <li><a href="/login">Login</a></li>
      {% endif %}
    </ul>
  </div>
</nav>
