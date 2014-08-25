# Copyright (c) 2013, Web Notes Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class TranslatedMessageValidation(Document):
	def before_insert(self):
		if frappe.db.get_value("Translated Message Validation",
			{"owner": self.owner, "message": self.message}):
			frappe.throw(_("You have already verifed"))

	def after_insert(self):
		frappe.db.sql("""update `tabTranslation Message`
			set verified = ifnull(verified, 0) + 1""")

		frappe.cache().delete_value("lang-data:" + frappe.db.get_value("Translated Message",
			self.message, "language"))

@frappe.whitelist()
def validate(message):
	frappe.db.get_doc({
		"doctype": "Translated Message Validation",
		"message": message
	}).insert()
