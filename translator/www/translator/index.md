# Translation Portal

<!-- jinja -->
<!-- no-sidebar -->
<p class="lead">Help translate ERPNext and other Frappe Apps. Click on a Language to Start</p>
<hr>
<div class="lang-list" style="max-width: 700px;">
	{% for lang in frappe.get_all("Language", fields=["*"], order_by = "name asc", limit_page_length=1000) %}
	{% if lang.name != "en" %}
	{% set info = get_info(lang.name) %}
	{% set percent = info.verified * 100 / (info.total + 1) %}
	<div class="lang row">
		<div class="col-sm-1">
			{{ lang.name }}
		</div>
		<div class="col-sm-3">
			<a href="/translator/view?lang={{ lang.name }}">{{ lang.language_name }}</a>
		</div>
		<div class="col-sm-8">
			<div class="progress">
				<div class="progress-bar" role="progressbar" aria-valuenow="60"
					aria-valuemin="0" aria-valuemax="100" style="width: {{ percent }}%;">
					<span class="sr-only">{{ percent }}% Verified</span>
				</div>
			</div>
			<p class="small text-muted" style="margin-top: -20px"
				>{{ info.edited or 0 }} messages edited. {{ info.verified }} verified of {{ info.total }}</p>
		</div>
	</div>
	{% endif %}
	{% endfor %}
</div>
