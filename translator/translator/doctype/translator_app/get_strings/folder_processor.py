import os

from .file_processor import FileProcessor

class FolderProcessor():

	def __init__(self, path) -> None:
		self.path = path

	def get_messages(self):
		messages = []
		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
				messages.extend(FolderProcessor(os.path.join(self.path, item)).get_messages())
			else:
				messages.extend(FileProcessor(os.path.join(self.path, item)).get_messages())
		return messages