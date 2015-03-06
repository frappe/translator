from __future__ import unicode_literals
import frappe
from frappe.frappeclient import FrappeClient

def migrate():
	print "connecting..."
	remote = FrappeClient("https://frappe.io", "Administrator", frappe.conf.frappe_admin_password)
	remote.migrate_doctype("User", exclude=["Guest", "Administrator"], preprocess=remove_undesired_roles)
	# remote.migrate_doctype("Language")
	# remote.migrate_doctype("Translator App")
	# remote.migrate_doctype("Source Message")
	# remote.migrate_doctype("Translated Message")
	# remote.migrate_doctype("Translated Message Validation")

def remove_undesired_roles(doc):
	doc["user_roles"] = [role for role in (doc.get("user_roles") or [])
		if role["role"] not in ("Knowledge Base Contributor", "Knowledge Base Editor", "Restriction Manager")]
