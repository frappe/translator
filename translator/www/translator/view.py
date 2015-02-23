import frappe

def get_context(context):
	query = """select source.name as source_name, source.message, 
	translated.name as translated_name, translated.translated, translated.verified, source.flagged,
	translated.modified, translated.modified_by, user.first_name, user.last_name from `tabSource Message` source 
	left join `tabTranslated Message` translated on (source.name=translated.source and translated.language = %s) 
	left join tabUser user on (translated.modified_by=user.name) {condition} and source.disabled !=1 order by source.message"""

	lang = frappe.form_dict.lang

	if frappe.form_dict.search:
		condition = "where source.message like %s"
		condition_value = '%' + frappe.form_dict.search + '%'
	
	else:
		c = frappe.form_dict.c or "*"
		if c == "*":
			condition = "where source.message REGEXP '^[^a-zA-Z]'"
			condition_value = None

		else:
			condition_value = c + '%'
			condition = "where source.message like %s"
	
	cond_tupple = (lang, condition_value) if condition_value else (lang,)

	context.messages = frappe.db.sql(query.format(condition=condition), cond_tupple, as_dict=True)

	context.parents = [
		{"title": "Community", "name":"community"},
		{"title": "Languages", "name":"translator"}
	]

