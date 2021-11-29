import json
import os

import frappe
from frappe.modules.import_file import read_doc_from_file
from frappe.translate import is_translatable
from frappe.utils import get_bench_path

from .file_processor import FileProcessor
from .folder_processor import FolderProcessor


class DoctypeProcessor:
	def __init__(self, path, doctype_name):
		self.path = path
		self.doctype_name = doctype_name

	def get_messages(self):
		messages = []

		try:
			doctype_json = read_doc_from_file(
				os.path.join(self.path, self.doctype_name + ".json")
			)
		except IOError:
			messages.extend(FolderProcessor(os.path.join(self.path)).get_messages())
			return messages

		messages.extend(
			[
				doctype_json.get("label"),
				doctype_json.get("description"),
				doctype_json.get("name"),
			]
		)

		for field in doctype_json.get("fields"):
			messages.extend([field.get("label"), field.get("description")])

			if field.get("fieldtype") == "Select" and field.get("options"):
				options = field.get("options").split("\n")
				if not "icon" in options[0]:
					messages.extend(options)
			if field.get("fieldtype") == "HTML" and field.get("options"):
				messages.append(field.get("options"))

		for d in doctype_json.get("permissions"):
			if d.get("role"):
				messages.append(d.get("role"))

		messages = [message for message in messages if message]
		messages = [
			("DocType: " + self.doctype_name, message)
			for message in messages
			if is_translatable(message)
		]

		messages = [
			{
				"position": os.path.join(self.path, self.doctype_name + ".json"),
				"source_text": message[1],
				"context": message[2] or "" if len(message) > 2 else "",
				"line_no": message[3] or 0 if len(message) == 4 else 0,
			}
			for message in messages
		]

		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(FolderProcessor(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(FileProcessor(os.path.join(self.path, item)).get_messages())

		for message in messages:
			message["type"] = "Document Type"
			message["document_name"] = frappe.unscrub(self.doctype_name)

		return messages
		# add workflow for doctype
