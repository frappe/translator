# Copyright (c) 2013, Web Notes Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class TranslatedMessage(Document):
	def validate(self):
		if self.verified > 0:
			if frappe.db.get_value("User", frappe.session.user, "karma") < 100:
				frappe.throw(_("Only user with more than 100 karma can edit verified translations"))

			self.verified = 0
