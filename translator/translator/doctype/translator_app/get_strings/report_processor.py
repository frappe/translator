
import json
import os
import re

import frappe
from frappe.modules.import_file import read_doc_from_file

from .file_processor import FileProcessor
from .folder_processor import FolderProcessor
from frappe.translate import is_translatable
from frappe.utils import get_bench_path



class ReportProcessor():
	def __init__(self, path, report_name):
		self.path = path
		self.report_name = report_name

	def get_messages(self):
		messages = []


		try:
			report_json = read_doc_from_file(os.path.join(self.path, self.report_name + '.json'))
		except IOError:
			messages.extend(FolderProcessor(os.path.join(self.path)).get_messages())
			return messages

		if report_json.get("roles"):
			for d in report_json.get("roles"):
				if d.get('role'):
					messages.append(d.get('role'))

		messages.extend([report_json.get('report_name'), report_json.get('name')])
		messages = [message for message in messages if message]
		messages = [('Report: ' + self.report_name, message) for message in messages if is_translatable(message)]


		if report_json.get('query'):
			messages.extend([(None, message) for message in re.findall('"([^:,^"]*):', report_json.get('query')) if is_translatable(message)])


		if report_json.get('json'):
			report_json = json.loads(report_json.get('json'))

			# if report_json.get('columns'):
			# 	context = "Column of report '%s'" % self.report_name # context has to match context in `prepare_columns` in query_report.js
			# 	messages.extend([(None, report_column[1], context) for report_column in report_json.get('columns')])

			# if report_json.get('filters'):
			# 	messages.extend([(None, report_filter.label) for report_filter in report_json.get('filters')])

			if report_json.get('query'):
				messages.extend([(None, message) for message in re.findall('"([^:,^"]*):', report_json.get('query')) if is_translatable(message)])


		messages = [
			{
				'position':os.path.relpath( os.path.join(self.path, self.report_name + '.json'), get_bench_path()),
				'source_text': message[1],
				'context' : message[2] or '' if len(message) > 2 else '',
				'line_no' : message[3] or 0 if len(message) == 4 else 0,
			}
			for message in messages
		]

		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(FolderProcessor(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(FileProcessor(os.path.join(self.path, item)).get_messages())

		for message in messages:
			message['type'] = 'Report'
			message['report'] = frappe.unscrub(self.report_name)

		return messages

