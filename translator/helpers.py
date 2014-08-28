from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def verify(message):
	frappe.get_doc({
		"doctype": "Translated Message Validation",
		"message": message
	}).insert(ignore_permissions=1)

@frappe.whitelist()
def update(message, translated):
	message = frappe.get_doc("Translated Message", message)
	message.translated = translated
	message.save(ignore_permissions=1)
