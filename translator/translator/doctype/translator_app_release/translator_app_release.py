# Copyright (c) 2021, Frappe Technologies and contributors
# For license information, please see license.txt
import os
import tarfile

import frappe
from frappe.website.website_generator import WebsiteGenerator
from translator.data import write_csv_for_all_languages
from frappe.utils import  get_site_path, random_string
from io import BytesIO as BIO

class TranslatorAppRelease(WebsiteGenerator):
	def validate(self):
		self.make_route()

	def create_release_job(self):
		frappe.get_doc({
			"doctype": "Translations Release Job",
			"translator_app_release": self.name
		}).save()




@frappe.whitelist()
def extract_strings_from_app(app_name):
	frappe.get_doc('Translator App', app_name).extract_strings_from_app()


@frappe.whitelist()
def create_release_job(release):
	frappe.get_doc('Translator App Release', release).create_release_job(),