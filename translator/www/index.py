import frappe

def get_context(context):
	context.get_info = frappe.get_attr("translator.helpers.get_info")
	context.parents =  [{"title":"Community", "name":"community"}]
	context.no_cache = 1
