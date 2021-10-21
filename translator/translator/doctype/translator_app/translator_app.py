# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, with_statement
import requests
import frappe
import os
import tarfile
from frappe.model.document import Document
from frappe.utils import  get_site_path, random_string

class TranslatorApp(Document):
	def validate(self):
		frappe.enqueue(
			self.create_source_strings,
			name=self.name,
			enqueue_after_commit=True,
		)
		self.status = 'Queued'

	def create_source_strings(self, name):
		frappe.db.set_value('Translator App', name, 'status', 'Validating Sources')

		for source in self.sources:
			r = requests.request('HEAD', f"https://api.github.com/repos/{self.owner}/{self.name}/tarball/{source.source}")
			if r.status_code != 200:
				frappe.db.set_value('Translator App', name, 'status', 'Failed')
				log = f'Source {source.source} Not Found. Make Sure that it is a branch or Tag'
				frappe.db.set_value('Translator App', name, 'log', log)
				return

		frappe.db.set_value('Translator App', name, 'status', 'Getting Code')

		for source in self.sources:


			r = requests.get( f"https://api.github.com/repos/{self.owner}/{self.name}/tarball/{source.source}", stream=True)

			self._prepare_clone_directory(source.source)

			file = tarfile.open(fileobj=r.raw, mode="r|gz")
			file.extractall(path=self.clone_directory)

			from translator.translator.doctype.translator_app.get_strings.process_app import ProcessApp
			messages = ProcessApp(
				os.path.join(self.clone_directory, 
				os.listdir(self.clone_directory)[0]
				), self.app_name).get_messages()

			# with open('messages.txt', 'w') as fp:
			# 	fp.write(str(len(messages)))

		frappe.db.set_value('Translator App', name, 'status', 'Successful')



	def _prepare_clone_directory(self, source):
		clone_directory  = get_site_path(frappe.db.get_single_value("Translation Settings", "clone_directory"))
		if not os.path.exists(clone_directory):
			os.mkdir(clone_directory)

		app_directory = os.path.join(clone_directory, self.app_name)
		if not os.path.exists(app_directory):
			os.mkdir(app_directory)

		source_directory = os.path.join(app_directory, source)
		if not os.path.exists(source_directory):
			os.mkdir(source_directory)

		self.clone_directory = os.path.join(
			clone_directory, self.app_name, source, random_string(7)
		)
		if not os.path.exists(clone_directory):
			os.mkdir(self.clone_directory)
