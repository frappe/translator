# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import strip
from frappe.model.document import Document

import re

class TranslatedMessage(Document):
	def autoname(self):
		self.name = frappe.generate_hash()