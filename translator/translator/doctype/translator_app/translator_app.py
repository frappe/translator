# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, with_statement

import frappe
import requests
from frappe.model.document import Document
from translator.data import translate_untranslated_from_google


class TranslatorApp(Document):
	def extract_strings_from_app(self):
		for source in self.sources:
			if source.disabled:
				continue
			frappe.get_doc(
				{
					"doctype": "Extract Strings Job",
					"translator_app": self.app_name,
					"translator_app_source": source.source,
				}
			).save()


@frappe.whitelist()
def extract_strings_from_app(app_name):
	frappe.get_doc("Translator App", app_name).extract_strings_from_app()


def extract_strings_weekly():
	for doc in get_weekly_string_extraction_candidates():
		doc = frappe.get_doc(
			{
				"doctype": "Extract Strings Job",
				"translator_app": doc.name,
				"translator_app_source": doc.source,
			}
		).save()


def get_weekly_string_extraction_candidates():
	TranslatorApp = frappe.qb.DocType("Translator App")
	TranslatorAppSource = frappe.qb.DocType("Translator App Source")
	return (
		frappe.qb.from_(TranslatorApp)
		.join(TranslatorAppSource)
		.on(TranslatorAppSource.parent == TranslatorApp.name)
		.where(
			(TranslatorAppSource.disabled == False)
			& (
				(TranslatorAppSource.extract_strings_weekly == True)
				| (TranslatorAppSource.strings_extracted == False)
			)
		)
		.select(TranslatorApp.name, TranslatorAppSource.source)
	).run(as_dict=True)


def translate_from_google():
	for lang in frappe.db.sql_list("select name from tabLanguage"):
		try:
			translate_untranslated_from_google(lang)
		except requests.exceptions.HTTPError:
			print("skipping {0}".format(lang))
			continue
		finally:
			frappe.db.commit()


def create_release_weekly():
	for doc in get_weekly_string_release_candidates():
		if release := release_exists(doc):
			print(release)
			frappe.get_doc("Translator App Release", release[0]).create_release_job()
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Translator App Release",
				"translator_app": doc.name,
				"repository_owner": doc.repository_owner,
				"translator_app_source": doc.source,
				"is_published": 1,
			}
		).save()
		doc.create_release_job()


def release_exists(doc):
	TranslatorAppRelease = frappe.qb.DocType("Translator App Release")
	return (
		frappe.qb.from_(TranslatorAppRelease)
		.where(
			(TranslatorAppRelease.translator_app == doc.name)
			& (TranslatorAppRelease.translator_app_source == doc.source)
			& (TranslatorAppRelease.repository_owner == doc.repository_owner)
		)
		.select(TranslatorAppRelease.name)
	).run(pluck="name")


def get_weekly_string_release_candidates():
	TranslatorApp = frappe.qb.DocType("Translator App")
	TranslatorAppSource = frappe.qb.DocType("Translator App Source")
	return (
		frappe.qb.from_(TranslatorApp)
		.join(TranslatorAppSource)
		.on(TranslatorAppSource.parent == TranslatorApp.name)
		.where(
			(TranslatorAppSource.disabled == False)
			& (TranslatorAppSource.release_weekly == True)
		)
		.select(
			TranslatorApp.name, TranslatorAppSource.source, TranslatorApp.repository_owner
		)
	).run(as_dict=True)
