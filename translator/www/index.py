import frappe

def get_context(context):
	context.get_info = frappe.get_attr("translator.helpers.get_info")
	context.parents =  [{"title":"Community", "name":"community"}]
	context.languages = frappe.get_all("Language", fields=["language_code", "language_name"])

	context.status_options = frappe.get_cached_value("DocField", {
		'parent': 'Contributed Translation',
		'fieldname': 'status'
	}, 'options').split('\n')

	context.contributed_tanslations = frappe.get_all("Contributed Translation",
		filters=frappe.form_dict, fields=["*"], limit_page_length=100)

	context.no_cache = 1
