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

@frappe.whitelist(allow_guest=True)
def add_translations(data):
	try:
		data = frappe._dict(json.loads(data))

		translation_map = data.translation_map

		for source_text, translation_dict in translation_map.items():
			translation_dict = frappe._dict(translation_dict)
			existing_doc_name = frappe.db.exists('Contributed Translation', {
				'source_name': source_text,
				'context': translation_dict.context,
				'contributor_email': data.contributor_email
			})
			if existing_doc_name:
				frappe.set_value('Contributed Translation', existing_doc_name, 'target_name', translation_dict.translated_text)
			else:
				doc = frappe.get_doc({
					'doctype': 'Contributed Translation',
					'source_string': source_text,
					'translated_string': translation_dict.translated_text,
					'context': translation_dict.context,
					'contributor_email': data.contributor_email,
					'contributor_name': data.contributor_name,
					'language': data.language
				})
				doc.insert(ignore_permissions = True)
	except Exception as e:
		print(e)

	return {
		"message": "Added to contribution list"
	}