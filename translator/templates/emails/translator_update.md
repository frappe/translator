<h4>Translation Updates!</h4>

<p>Translators,</p>

<p>Here is a quick update of translation activity this week:</p>

<table style="width: 100%" cellspacing="0px" border="1px">
	<thead>
		<tr>
			<th style="width: 10%">
			</th>
			<th style="width: 20%">
			</th>
			<th style="width: 35%">
				This Week
			</th>
			<th style="width: 35%">
				Total
			</th>
		</tr>
	</thead>
	<tbody>
	{% for lang in frappe.db.sql("""select * from tabLanguage order by name asc""", as_dict=True) %}
	{% if lang.name != "en" %}
	{% set info = frappe.get_attr("translator.helpers.get_info")(lang.name) %}
	{% set week = frappe.get_attr("translator.helpers.get_info")(lang.name, this_week=True) %}
	<tr>
		<td>
			{{ lang.name }}
		</td>
		<td>
			<a href="/translator/view?lang={{ lang.name }}">{{ lang.language_name }}</a>
		</td>
		<td>
			{{ week.edited or 0 }} Edited
			<br>{{ week.verified or 0 }} Verified
		</td>
		<td>
			{{ info.edited or 0 }}
			<br>{{ info.verified or 0 }}
		</td>
	</tr>
	{% endif %}
	{% endfor %}
	</tbody>
</table>
