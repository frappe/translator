import json
import os

import frappe
from frappe.modules.import_file import read_doc_from_file
from frappe.translate import is_translatable
from frappe.utils import get_bench_path

from .file_processor import FileProcessor
from .folder_processor import FolderProcessor


class PageProcessor:
	def __init__(self, path, page_name):
		self.path = path
		self.page_name = page_name

	def get_messages(self):
		messages = []

		try:
			page_json = read_doc_from_file(os.path.join(self.path, self.page_name + ".json"))
		except IOError:
			messages.extend(FolderProcessor(os.path.join(self.path)).get_messages())
			return messages

		messages.extend(
			[page_json.get("title"), page_json.get("page_name"), page_json.get("name")]
		)

		for d in page_json.get("roles"):
			if d.get("role"):
				messages.append(d.get("role"))

		messages = [message for message in messages if message]
		messages = [
			(os.path.join(self.path, self.page_name + ".json"), message)
			for message in messages
			if is_translatable(message)
		]

		messages = [
			{
				"position": os.path.join(self.path, self.page_name + ".json"),
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
			message["type"] = "Page"
			message["document_name"] = frappe.unscrub(self.page_name)

		return messages
