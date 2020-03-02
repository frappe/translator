# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
import frappe

class ContributedTranslation(Document):
	def on_update(self):
		frappe.cache().hdel('contributed_translations', self.language)
		if self.status == 'Verified':
			self.verified = 1
