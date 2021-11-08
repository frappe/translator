from genericpath import isdir
import os
import re

import frappe

from .file_processor import FileProcessor
from .folder_processor import FolderProcessor
from .doctype_processor import DoctypeProcessor
from .report_processor import ReportProcessor
from .page_processor import PageProcessor

IGNORED_ITEMS = ['']


class ModuleProcessor:
	def __init__(self, path, module_name):
		self.path = path
		self.module_name = module_name

	def get_messages(self):

		messages = []
		for item in os.listdir(self.path):
			if item == 'doctype':
				for doctype in os.listdir(os.path.join(self.path, item)):
					if doctype in ('__pycache__'):
						continue
					if isdir(os.path.join(self.path, item, doctype)):
						messages.extend(DoctypeProcessor(os.path.join(self.path, item, doctype), doctype).get_messages())
					else:
						messages.extend(FileProcessor(os.path.join(self.path, item, doctype)).get_messages())
			elif item == 'report':
				for report in os.listdir(os.path.join(self.path, item)):
					if report in ('__pycache__'):
						continue
					if isdir(os.path.join(self.path, item, report)) and report not in ('__pycache__'):
						messages.extend(ReportProcessor(os.path.join(self.path, item, report), report).get_messages())
					else:
						messages.extend(FileProcessor(os.path.join(self.path, item, report)).get_messages())
			elif item == 'page':
				for page in os.listdir(os.path.join(self.path, item)):
					if page in ('__pycache__'):
						continue
					if isdir(os.path.join(self.path, item, page)):
						messages.extend(ProcessPage(os.path.join(self.path, item, page), page).get_messages())
					else:
						messages.extend(FileProcessor(os.path.join(self.path, item, page)).get_messages())
			elif os.path.isdir(os.path.join(self.path, item)):
				messages.extend(FolderProcessor(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(FileProcessor(os.path.join(self.path, item)).get_messages())


		for message in messages:
			message['module'] = frappe.unscrub(self.module_name)

		return messages


