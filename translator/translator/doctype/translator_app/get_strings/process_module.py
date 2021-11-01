from genericpath import isdir
import os
import re

import frappe

from .process_file import ProcessFile
from .process_folder import ProcessFolder
from .process_doctype import ProcessDoctype
from .process_report import ProcessReport
from .process_page import ProcessPage

IGNORED_ITEMS = ['']


class ProcessModule:
	def __init__(self, path, module_name):
		self.path = path
		self.module_name = module_name

	def get_messages(self):

		messages = []

		for item in os.listdir(self.path):
			if item == 'doctype':
				for doctype in os.listdir(os.path.join(self.path, item)):
					if isdir(os.path.join(self.path, item, doctype)) and doctype not in ('__pycache__'):
						print("inside doctype", doctype)

						messages.extend(ProcessDoctype(os.path.join(self.path, item, doctype), doctype).get_messages())
			elif item == 'report':

				for report in os.listdir(os.path.join(self.path, item)):
					if isdir(os.path.join(self.path, item, report)) and report not in ('__pycache__'):
						print("inside report", report)

						messages.extend(ProcessReport(os.path.join(self.path, item, report), report).get_messages())
			elif item == 'page':
				for page in os.listdir(os.path.join(self.path, item)):
					if isdir(os.path.join(self.path, item, page)) and page not in ('__pycache__'):
						print("inside page", page)
						messages.extend(ProcessPage(os.path.join(self.path, item, page), page).get_messages())
			elif os.path.isdir(os.path.join(self.path, item)):
				print('inside folder', item )
				messages.extend(ProcessFolder(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)).get_messages())


		for message in messages:
			message['module'] = frappe.unscrub(self.module_name)

		return messages


