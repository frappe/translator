# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from translator.data import get_translation_from_google

class SourceMessage(Document):
	def autoname(self):
		self.name = frappe.generate_hash()

	def on_update(self):
		frappe.cache().delete_key('source_messages')

	def on_trash(self):
		frappe.cache().delete_key('source_messages')

	def after_insert(self):
		frappe.cache().delete_key('source_messages')
		# frappe.enqueue_doc(self.doctype, self.name, 'create_google_translations')

	def create_google_translations(self):
		langs = frappe.db.sql_list("select name from tabLanguage")
		try:
			for lang in langs:
				create_translation(lang, self)
		except:
			pass

def create_translation(lang, source_dict):
	t = frappe.new_doc('Translated Message')
	t.translation_source = 'Google Translated'
	t.language = lang
	t.source = source_dict.name
	try:
		t.translated = get_translation_from_google(lang, source_dict.message)
		t.save()
	except requests.exceptions.HTTPError:
		print("Skipping {0}".format(lang))
	except frappe.exceptions.ValidationError:
		pass