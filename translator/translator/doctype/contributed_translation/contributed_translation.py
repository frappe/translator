# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import semantic_version, subprocess

class ContributedTranslation(Document):
	pass

def push_contributions_to_respected_versions():
	if not frappe.conf.enabled_for_translation_contributions:
		return

	for translation in frappe.get_all("Contributed Translation",
		{"pushed_to_respective_bench": 0}, "*"):

		major_version = get_major_version(translation.version)

		if not major_version:
			continue

		bench_details = get_bench_details(major_version)

		try:
			subprocess.check_output(['bench', '--site', bench_details.site, 'update-contributions',
				translation.source_string, translation.translated_string, translation.app_name,
				translation.version, language], cwd=bench_details.bench_path)
			frappe.db.set_value("Contributed Translation", translation.name, 'pushed_to_respective_bench', 1)
		except subprocess.CalledProcessError as err:
			frappe.log_error(err.output)

def get_bench_details(version):
	return frappe._dict(frappe.conf.bench_details.get('version', {}))

def get_major_version(version):
	try:
		v = semantic_version.Version(version)
		return v.major
	except ValueError as e:
		return ''
