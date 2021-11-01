# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, with_statement

import frappe
from frappe.model.document import Document
class TranslatorApp(Document):
	def extract_strings_from_app(self):
		for source in self.sources:
			frappe.get_doc({
				"doctype": "Extract Strings Job",
				"translator_app": self.app_name,
				"translator_app_source": source.source
			}).save()

@frappe.whitelist()
def extract_strings_from_app(app_name):
	print("app_name" * 255)
	frappe.get_doc('Translator App', app_name).extract_strings_from_app()
