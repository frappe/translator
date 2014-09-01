### Translation Updates!

Translators,

Here is a quick update of translation activity this week:

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
			{{ week.edited or 0 }} / {{ week.total }} Edited
			<br>{{ week.veified or 0 }} / {{ week.total }} Verified
		</td>
		<td>
			{{ info.edited or 0 }} / {{ info.total }} Edited
			<br>{{ info.veified or 0 }} / {{ info.total }} Verified
		</td>
	</tr>
	{% endif %}
	{% endfor %}
	</tbody>
</table>
