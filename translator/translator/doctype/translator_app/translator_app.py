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
	frappe.get_doc('Translator App', app_name).extract_strings_from_app()

def extract_strings_weekly():
	for release in frappe.get_all('Translator App', ['name'], [['weekly_string_extraction','=', True]], pluck = 'name'):
		extract_strings_from_app(release)


from translator.data import (import_source_messages, export_untranslated_to_json,
import_translations_from_csv, translate_untranslated_from_google, get_apps_to_be_translated)
import requests


def translate_from_google():
	for lang in frappe.db.sql_list("select name from tabLanguage"):
		try:
			translate_untranslated_from_google(lang)
		except requests.exceptions.HTTPError:
			print("skipping {0}".format(lang))
			continue
		finally:
			frappe.db.commit()