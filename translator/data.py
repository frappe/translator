# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe, os

def import_languages():
	with open(frappe.get_app_path("frappe", "data", "languages.txt"), "r") as f:
		for l in unicode(f.read(), "utf-8").splitlines():
			if l:
				code, name = l.strip().split(None, 1)
				if not frappe.db.exists("Language", code):
					print "inserting " + code
					frappe.get_doc({
						"doctype":"Language",
						"language_code": code,
						"language_name": name
					}).insert()

		frappe.db.commit()

def import_translations():
	apps_path = frappe.get_app_path("frappe", "..", "..")
	for app in os.listdir(apps_path):
		translations_folder = os.path.join(apps_path, app, app, "translations")
		if os.path.exists(translations_folder):
			for l in frappe.db.sql_list("select name from tabLangauges"):
				pass


def export_translations():
	pass
