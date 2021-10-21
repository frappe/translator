
import json
import os
import re

import frappe
from frappe.modules.import_file import read_doc_from_file

from .process_file import ProcessFile
from .process_folder import ProcessFolder



class ProcessReport():
	def __init__(self, path, report_name):
		self.path = path
		self.report_name = report_name

	def get_messages(self):
		messages = []
		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(ProcessFolder(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)).get_messages())

		try:
			report_json = read_doc_from_file(os.path.join(self.path, self.report_name + '.json'))
		except IOError:
			return messages

		if report_json.get("roles"):
			for d in report_json.get("roles"):
				if d.get('role'):
					messages.append(d.get('role'))

		messages.extend([report_json.get('report_name'), report_json.get('name')])

		if report_json.get(json):
			report_json = json.loads(report_json.get(json))

			if report_json.get('columns'):
				context = "Column of report '%s'" % self.report_name # context has to match context in `prepare_columns` in query_report.js
				messages.extend([(None, report_column.label, context) for report_column in report_json.get('columns')])

			if report_json.get('filters'):
				messages.extend([(None, report_filter.label) for report_filter in report_json.get('filters')])

			if report_json.get('query'):
				messages.extend([(None, message) for message in re.findall('"([^:,^"]*):', report_json.get('query')) if is_translatable(message)])

		return messages

def is_translatable(m):
	if re.search("[a-zA-Z]", m) and not m.startswith("fa fa-") and not m.endswith("px") and not m.startswith("eval:"):
		return True
	return False