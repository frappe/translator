import frappe
import json

@frappe.whitelist(allow_guest=True)
def add_translation(data):
	data = json.loads(data)
	if frappe.db.get_all("Contributed Translation", filters={"source_string": data.get("source_name"), "translated_string": data.get("target_name"), "language": data.get("language")}):
		return "Already exists"
	else:
		contributed_translation = frappe.get_doc({
			"doctype": "Contributed Translation",
			"language": data.get("language"),
			"contributor": data.get("contributor"),
			"source_string": data.get("source_name"),
			"translated_string": data.get("target_name"),
			"posting_date": data.get("posting_date")
		}).insert(ignore_permissions = True)
		return "Added to contribution list"
