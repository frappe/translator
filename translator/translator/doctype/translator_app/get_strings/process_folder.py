import os

from .process_file import ProcessFile

class ProcessFolder():

	def __init__(self, path) -> None:
		self.path = path

	def get_messages(self):
		messages = []
		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(ProcessFolder(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(ProcessFile(os.path.join(self.path, item)).get_messages())
		return messages