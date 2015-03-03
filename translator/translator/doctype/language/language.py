# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Language(Document):
	pass

def clear_cache():
	for lang in frappe.db.sql_list("select name from tabLanguage"):
		frappe.cache().delete_value("lang-data:" + lang)
