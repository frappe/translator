# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SourceMessage(Document):
	def autoname(self):
		self.name = frappe.generate_hash()
