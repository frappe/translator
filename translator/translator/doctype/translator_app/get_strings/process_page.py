import json
import os

import frappe
from frappe.modules.import_file import read_doc_from_file
from frappe.translate import is_translatable

from .process_file import ProcessFile
from .process_folder import ProcessFolder



class ProcessPage():
	def __init__(self, path, page_name):
		self.path = path
		self.page_name = page_name

	def get_messages(self):
		messages = []
		page_json = read_doc_from_file(os.path.join(self.path, self.page_name + '.json'))

		messages.extend([page_json.get('title'), page_json.get('page_name')])

		for d in page_json.get("roles"):
			if d.get('role'):
				messages.append(d.get('role'))

		messages = [message for message in messages if message]
		messages = [(os.path.join(self.path, self.page_name + '.json'), message) for message in messages if is_translatable(message)]


		messages = [
			{
				'position': os.path.join(self.path, self.page_name + '.json'),
				'source_text': message[1],
				'context' : message[2] or '' if len(message) > 2 else '',
				'line_no' : message[3] or 0 if len(message) == 4 else 0,
			}
			for message in messages
		]


		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(ProcessFolder(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)).get_messages())

		for message in messages:
			message['type'] = 'Page'
			message['page'] = frappe.unscrub(self.page_name)

		return messages