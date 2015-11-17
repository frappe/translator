# Copyright (c) 2015, Frappe Technologies and contributors
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
		frappe.db.sql("""update `tabTranslated Message`
			set verified = verified + 1 where name=%s""", self.message)

		user = frappe.db.get_value("Translated Message", self.message, "modified_by")
		if user==frappe.session.user:
			frappe.throw("You can't verify your own edits!")
		if user != "Administrator":
			frappe.db.sql("""update `tabUser`
				set karma = karma + 1 where name=%s""", user)

		frappe.cache().delete_value("lang-data:" + frappe.db.get_value("Translated Message",
			self.message, "language"))

