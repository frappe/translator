import json
import os

import frappe
from frappe.modules.import_file import read_doc_from_file

from .process_file import ProcessFile
from .process_folder import ProcessFolder


class ProcessDoctype():
	def __init__(self, path, doctype_name):
		self.path = path
		self.doctype_name = doctype_name

	def get_messages(self):
		messages = []
		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(ProcessFolder(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)).get_messages())

		try:
			doctype_json = read_doc_from_file(os.path.join(self.path, self.doctype_name + '.json'))
		except IOError:
			return messages

		messages.extend([doctype_json.get('label'), doctype_json.get('description')])

		for field in doctype_json.get('fields'):
			messages.extend([field.get('label'), field.get('description')])

			if field.get('fieldtype')=='Select' and field.get('options'):
				options = field.get('options').split('\n')
				if not "icon" in options[0]:
					messages.extend(options)
			if field.get('fieldtype')=='HTML' and field.get('options'):
				messages.append(field.get('options'))

		for d in doctype_json.get("permissions"):
			if d.get('role'):
				messages.append(d.get('role'))

		return messages
		# add workflow for doctype
