import frappe

def get_context(context):
	context.messages = frappe.db.sql("""select t1.name, t1.source, t1.translated, t1.verified,
	t1.flagged, t1.modified, t1.modified_by, t2.first_name, t2.last_name
	from `tabTranslated Message` t1, tabUser t2
	where t1.language = %s and t1.source like %s and t2.name = t1.modified_by
	order by t1.source""", (frappe.form_dict.lang, (frappe.form_dict.c or "A") + "%"), as_dict=True)

	context.parents = [
		{"title": "Community", "name":"community"},
		{"title": "Languages", "name":"translator"}
	]
