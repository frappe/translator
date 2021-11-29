import os

import frappe
from frappe.utils import get_bench_path

from .file_processor import FileProcessor
from .folder_processor import FolderProcessor
from .module_processor import ModuleProcessor

MODULES_FILE = "modules.txt"

IGNORED_ITEMS = [
	"change_log",
	"demopatches",
	"translations",
	"modules.txt",
	"patches.txt",
]


class AppProcessor:
	def __init__(self, path, app_name):
		self.path = os.path.join(path, app_name)
		self.app_name = app_name

	def get_messages(self):
		messages = []

		modules = frappe.get_file_items(os.path.join(self.path, MODULES_FILE))

		[
			messages.append(
				{
					"position": os.path.join(self.path, MODULES_FILE),
					"source_text": module,
					"context": "Module Name",
					"line_no": 0,
				}
			)
			for module in modules
		]

		modules = [frappe.scrub(module) for module in modules]
		for item in os.listdir(self.path):
			if item in IGNORED_ITEMS:
				continue
			elif item in modules:
				messages.extend(ModuleProcessor(os.path.join(self.path, item), item).get_messages())
			elif os.path.isdir(os.path.join(self.path, item)):
				messages.extend(FolderProcessor(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(FileProcessor(os.path.join(self.path, item)).get_messages())
		return messages
