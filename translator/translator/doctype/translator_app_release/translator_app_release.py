# Copyright (c) 2021, Frappe Technologies and contributors
# For license information, please see license.txt
import os
import tarfile

import frappe
from frappe.website.website_generator import WebsiteGenerator
from io import BytesIO as BIO


class TranslatorAppRelease(WebsiteGenerator):
	def validate(self):
		self.make_route()

	def create_release_job(self):
		frappe.get_doc(
			{"doctype": "Translations Release Job", "translator_app_release": self.name}
		).save()

	def get_context(self, context):
		link = frappe.get_all(
			"File",
			fields=["file_url"],
			filters={"attached_to_name": self.name, "attached_to_doctype": self.doctype},
			pluck="file_url",
			order_by="modified desc",
			limit=1,
		)

		redirect_url = link[0]
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = redirect_url
		raise frappe.Redirect

	def make_route(self):
		self.route = f"translation/{self.repository_owner}/{self.translator_app}/{self.translator_app_source}"


@frappe.whitelist()
def create_release_job(release):
	frappe.get_doc("Translator App Release", release).create_release_job(),
