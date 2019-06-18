import frappe
import json

@frappe.whitelist(allow_guest=True)
def add_translation(data):
	data = json.loads(data)
	if frappe.db.get_all("Contributed Translation", filters={"source_string": data.get("source_name"), "translated_string": data.get("target_name"), "language": data.get("language")}):
		return {
			"message": "Already exists"
		}
	else:
		contributed_translation = frappe.get_doc({
			"doctype": "Contributed Translation",
			"language": data.get("language"),
			"contributor": data.get("contributor"),
			"source_string": data.get("source_name"),
			"translated_string": data.get("target_name"),
			"posting_date": data.get("posting_date")
		}).insert(ignore_permissions = True)
		return {
			"message": "Added to contribution list",
			"doc_name": contributed_translation.name
		}

@frappe.whitelist(allow_guest=True)
def translation_status(data):
	data = json.loads(data)
	status = frappe.db.get_value("Contributed Translation", data.get("doc_name"), "status")
	if status:
		return {
			"status": status
		}
	else:
		return {
			"message": "Contributed Translation has been deleted"
		}
