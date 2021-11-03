import os

import frappe

from .process_module import ProcessModule
from .process_folder import ProcessFolder
from .process_file import ProcessFile
from frappe.utils import get_bench_path


MODULES_FILE = 'modules.txt'

IGNORED_ITEMS = ['change_log', 'demo' 'patches',  'translations', 'modules.txt', 'patches.txt']



class ProcessApp:

	def __init__(self, path, app_name):
		self.path = os.path.join(path, app_name)
		self.app_name = app_name

	def get_messages(self):
		messages = []

		modules = frappe.get_file_items(os.path.join(self.path, MODULES_FILE))

		[
			messages.append({
				'position': os.path.relpath(os.path.join(self.path, MODULES_FILE), get_bench_path()) ,
				'source_text': module,
				'context' : 'Module Name',
				'line_no' : 0
			})
			for module in modules
		]

		modules = [frappe.scrub(module)  for module in modules]
		for item in os.listdir(self.path):
			if item in IGNORED_ITEMS:
				continue
			elif item in modules:
				messages.extend(ProcessModule(os.path.join(self.path, item), item).get_messages())
			elif os.path.isdir(os.path.join(self.path, item)):
				messages.extend(ProcessFolder(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)).get_messages())
		return messages