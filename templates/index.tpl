{% if user %}
home for {{ user['username'] }}
<br/><a href="/settings">settings</a>
<br/><a href="/logout">logout</a>
{% else %}
<a href="/login">login</a>
{% endif %}