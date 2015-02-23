# Copyright (c) 2013, Web Notes Technologies and Contributors
# See license.txt

import frappe
import unittest

test_records = frappe.get_test_records('Source Message')

class TestSourceMessage(unittest.TestCase):
	pass
