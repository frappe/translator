import os

from .process_file import ProcessFile
from .process_folder import ProcessFolder
from .process_doctype import ProcessDoctype
from .process_report import ProcessReport
from .process_page import ProcessPage

IGNORED_ITEMS = ['']


class ProcessModule:
	def __init__(self, path, app_name):
		self.path = path
		self.app_name = app_name

	def get_messages(self):

		messages = []

		for item in os.listdir(self.path):
			if item == 'doctype':
				messages.extend(ProcessDoctype(os.path.join(self.path, item), item))
			elif item == 'report':
				messages.extend(ProcessReport(os.path.join(self.path, item), item))
			elif item == 'page':
				messages.extend(ProcessPage(os.path.join(self.path, item), item))
			elif os.path.isdir(os.path.join(self.path, item)):
				messages.extend(ProcessFolder(os.path.join(self.path, item)))
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)))

		return messages