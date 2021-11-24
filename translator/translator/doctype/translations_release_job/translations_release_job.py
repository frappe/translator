# Copyright (c) 2021, Frappe Technologies and contributors
# For license information, please see license.txt

import os
import tarfile
import frappe
from frappe.model.document import Document
from translator.data import write_csv_for_all_languages
from frappe.utils import  get_site_path, random_string
from io import BytesIO as BIO

class TranslationsReleaseJob(Document):
	def validate(self):
		print(frappe.enqueue(
			self.create_release_wrapper,
			enqueue_after_commit=True,
			queue='long',
			job_name=f'Release translations for {self.repository_owner}/{self.translator_app}@{self.translator_app_source}'
		))


	def get_endpoint(self):
		return f"https://api.github.com/repos/{self.repository_owner}/{self.translator_app}/tarball/{self.translator_app_source}"

	def create_release_wrapper(self):
		try:
			self.create_release()
		except Exception:
			self.create_log()

	def set_status(self, status):
		frappe.db.set_value('Translations Release Job', self.name, 'status', status)
		frappe.db.commit()


	def create_log(self, message = None):
		self.set_status('Failed')
		log = message + str(frappe.get_traceback()) if message else str(frappe.get_traceback())
		frappe.db.set_value('Translations Release Job', self.name, 'failure_log', log)

	def create_release(self):
		self.set_status('Preparing')
		self._prepare_clone_directory(self.translator_app_source)
		self.set_status('Writing Files')
		write_csv_for_all_languages(self.translator_app, self.clone_directory)
		self.create_tar()
		self.set_status('Releasing')
		self.create_file_doc()
		self.set_status('Completed')

	def get_context(self, context):

		link = frappe.get_all("File", fields=["file_url"],
		filters = {"attached_to_name": self.name, "attached_to_doctype": self.doctype},
		pluck = 'file_url', order_by='modified desc', limit = 1 )

		redirect_url = link[0]
		frappe.local.response['type'] = 'redirect'
		frappe.local.response['location'] = redirect_url
		raise frappe.Redirect

	def create_tar(self):

		file_out = BIO()
		tar = tarfile.open(mode = "w:gz", fileobj = file_out)
		tar.add(self.clone_directory, arcname=self.random + 'random')
		# for p in path:
		# 	tar.add(p)
		tar.close()
		self.tar = file_out.getvalue()

	def create_file_doc(self):
		ret = frappe.get_doc({
			"doctype": "File",
			"attached_to_doctype": 'Translator App Release',
			"attached_to_name": self.translator_app_release,
			# "attached_to_field": fieldname,
			# "folder": folder,
			"file_name": self.random + '.tar.gz',
			"file_url": self.random + '.tar.gz',
			"is_private": 0,
			"content": self.tar
		})
		ret.save(ignore_permissions=True)
		frappe.db.sql("""Update  `tabFile`
			set attached_to_name = '' where attached_to_doctype = 'Translator App Release' and attached_to_name = %s and name != %s"""
			,[self.translator_app_release, ret.name])

	def _prepare_clone_directory(self, source):
		clone_directory  = get_site_path(frappe.db.get_single_value("Translation Settings", "translation_dumps"))
		if not os.path.exists(clone_directory):
			os.mkdir(clone_directory)

		app_directory = os.path.join(clone_directory, self.translator_app)
		if not os.path.exists(app_directory):
			os.mkdir(app_directory)

		source_directory = os.path.join(app_directory, source)
		if not os.path.exists(source_directory):
			os.mkdir(source_directory)
		self.random = random_string(7)
		self.clone_directory = os.path.join(
			clone_directory, self.translator_app, source, self.random
		)
		print(os.path.exists(self.clone_directory))
		print(self.clone_directory)
		if not os.path.exists(self.clone_directory):
			print(os.mkdir(self.clone_directory))
		print(os.path.exists(self.clone_directory))