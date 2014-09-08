# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe, os

from frappe.translate import read_csv_file, get_all_languages, write_translations_file

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
			for lang in frappe.db.sql_list("select name from tabLanguage"):
				path = os.path.join(translations_folder, lang + ".csv")
				if os.path.exists(path):
					print "Evaluating {0}...".format(lang)
					data = read_csv_file(path)
					for m in data:
						if not frappe.db.get_value("Translated Message",
							{"language": lang, "source": m[0]}):
							frappe.get_doc({
								"doctype": "Translated Message",
								"language": lang,
								"source": m[0],
								"translated": m[1],
								"verfied": 0
							}).insert()
							frappe.db.commit()
				else:
					print path + " does not exist"


def export_translations():
	for lang in get_all_languages():
		if lang!="en":
			print "exporting " + lang
			full_dict = dict(frappe.db.sql("""select source, translated
				from `tabTranslated Message` where language=%s""", lang))
			for app in frappe.get_all_apps(True):
				write_translations_file(app, lang, full_dict, sorted(full_dict.keys()))

