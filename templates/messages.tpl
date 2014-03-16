{% macro list_messages(messages) -%}
  {% for message in messages %}
    {{ message | e }}<br/>
  {% endfor %}
{%- endmacro %}

{% if messages['info'] %}
  <div class="alert alert-success">{{ list_messages(messages['info']) }}</div>
{% endif %}

{% if messages['error'] %}
  <div class="alert alert-danger">{{ list_messages(messages['error']) }}</div>
{% endif %}
