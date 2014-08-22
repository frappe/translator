# Copyright (c) 2013, Web Notes Technologies and Contributors
# See license.txt

import frappe
import unittest

test_records = frappe.get_test_records('Translated Message')

class TestTranslatedMessage(unittest.TestCase):
	pass
