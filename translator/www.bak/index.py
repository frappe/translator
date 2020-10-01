import frappe

languages = frappe.get_all("Language", fields=["language_code", "language_name"])

def get_context(context):
	context.get_info = frappe.get_attr("translator.helpers.get_info")
	context.parents =  [{"title":"Community", "name":"community"}]
	context.languages = languages

	context.language_labels = {lang.language_code: lang.language_name for lang in languages}

	context.status_options = frappe.get_cached_value("DocField", {
		'parent': 'Contributed Translation',
		'fieldname': 'status'
	}, 'options').split('\n')

	context.contributed_translations = frappe.get_all("Contributed Translation",
		filters=frappe._dict(frappe.form_dict),
		fields=['language', 'source_string', 'translated_string', 'status'],
		limit_page_length=100)

	context.no_cache = 1
