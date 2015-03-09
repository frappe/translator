import frappe

def get_context(context):
	query = """select source.name as source_name, source.message, 
	translated.name as translated_name, translated.translated, translated.verified, source.flagged,
	translated.modified, translated.modified_by, user.first_name, user.last_name from `tabSource Message` source 
	left join `tabTranslated Message` translated on (source.name=translated.source and translated.language = %s) 
	left join tabUser user on (translated.modified_by=user.name) where {condition} and source.disabled !=1 order by source.message"""

	lang = frappe.form_dict.lang

	if frappe.form_dict.search:
		condition = "(source.message like %s or translated.translated like %s)"
		condition_values = ['%' + frappe.form_dict.search + '%', '%' + frappe.form_dict.search + '%']
	
	else:
		c = frappe.form_dict.c or "*"
		if c == "*":
			condition = "source.message REGEXP '^[^a-zA-Z]'"
			condition_values = None

		else:
			condition = "source.message like %s"
			condition_values = [c + '%']
	
	cond_tuple = tuple([lang] + condition_values) if condition_values else (lang,)

	context.messages = frappe.db.sql(query.format(condition=condition), cond_tuple, as_dict=True)

	context.parents = [
		{"title": "Community", "name":"community"},
		{"title": "Languages", "name":"translator"}
	]

