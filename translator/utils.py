import frappe

def set_default_role(doc, method):

	if frappe.flags.setting_role or frappe.flags.in_migrate:
		return

	doc.add_roles('Verifier')
