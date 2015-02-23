# Copyright (c) 2013, Web Notes Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class TranslatedMessage(Document):
	def autoname(self):
		self.name = frappe.generate_hash()
	
	def before_insert(self):
		if frappe.db.count("Translated Message", {"source": self.source, "language":self.language}):
			raise frappe.ValidationError("Translated Message for this source message already exists")

	def validate(self):
		if self.verified > 0:
			if frappe.db.get_value("User", frappe.session.user, "karma") < 100:
				frappe.throw(_("Only user with more than 100 karma can edit verified translations"))

			self.verified = 0

def on_doctype_update():
	frappe.db.add_index("Translated Message", ["language", "source(10)"])
