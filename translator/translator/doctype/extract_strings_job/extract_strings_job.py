# Copyright (c) 2021, Frappe Technologies and contributors
# For license information, please see license.txt

import os
import tarfile

import requests


import frappe
from frappe.model.document import Document

from frappe.utils import  get_site_path, random_string


class ExtractStringsJob(Document):
	def validate(self):
		frappe.enqueue(
			self.create_source_strings_wrapper,
			enqueue_after_commit=True,
			queue='long',
			job_name=f'Extract strings from {self.repository_owner}/{self.translator_app}@{self.translator_app_source}'
		)


	def get_endpoint(self):
		return f"https://api.github.com/repos/{self.repository_owner}/{self.translator_app}/tarball/{self.translator_app_source}"

	def create_source_strings_wrapper(self):
		try:
			self.set_status('Validating')
			self.create_source_strings()
		except Exception:
			self.create_log()

	def set_status(self, status):
		frappe.db.set_value('Extract Strings Job', self.name, 'status', status)
		frappe.db.commit()


	def create_log(self, message = None):
		self.set_status('Failed')
		log = message + str(frappe.get_traceback()) if message else str(frappe.get_traceback())
		frappe.db.set_value('Extract Strings Job', self.name, 'failure_log', log)


	def create_source_strings(self):

		r = requests.request('HEAD', self.get_endpoint())
		if r.status_code != 200:
			message = f'Source {self.translator_app_source} Not Found. Make Sure that it is a branch or Tag'
			self.create_log(message)
			return

		self.set_status('Extracting Strings')



		r = requests.get( self.get_endpoint(), stream=True)

		self._prepare_clone_directory(self.translator_app_source)

		file = tarfile.open(fileobj=r.raw, mode="r|gz")
		file.extractall(path=self.clone_directory)

		from translator.translator.doctype.translator_app.get_strings.process_app import ProcessApp
		messages = ProcessApp(
			os.path.join(self.clone_directory,
			os.listdir(self.clone_directory)[0]
			), self.translator_app).get_messages()

		# with open('messages.txt', 'w') as fp:
		# 	fp.write(str(len(messages)))

		formatted_messages = get_formatted_messages(messages, self.translator_app, self.translator_app_source)
		import_source_messages(formatted_messages, self.translator_app)

		self.set_status('Completed')




	def _prepare_clone_directory(self, source):
		clone_directory  = get_site_path(frappe.db.get_single_value("Translation Settings", "clone_directory"))
		if not os.path.exists(clone_directory):
			os.mkdir(clone_directory)

		app_directory = os.path.join(clone_directory, self.translator_app)
		if not os.path.exists(app_directory):
			os.mkdir(app_directory)

		source_directory = os.path.join(app_directory, source)
		if not os.path.exists(source_directory):
			os.mkdir(source_directory)

		self.clone_directory = os.path.join(
			clone_directory, self.translator_app, source, random_string(7)
		)
		if not os.path.exists(clone_directory):
			os.mkdir(self.clone_directory)



def import_source_messages(message_map, name):
	"""Import messages from apps listed in **Translator App** as **Source Message**"""
	l = len(message_map)
	# frappe.db.set_value('Translator App', name, 'log', message_map)

	# frappe.db.sql("UPDATE `tabSource Message` SET `disabled`=1")
	for i, ((message, context), positions) in enumerate(message_map.items()):
		# used SQL so as to make message comparision case sensitive

		# try:

		source_message = frappe.db.sql("""
			SELECT `name`
			FROM `tabSource Message`
			WHERE `message` = BINARY %s AND coalesce(`tabSource Message`.context, '') = %s
			LIMIT 1
		""", (message, context), as_dict=1)


		source_message = source_message[0] if source_message else None
		if source_message:
			d = frappe.get_doc("Source Message", source_message['name'])
			d.disabled = 0
			positions = get_postions_to_save(d.positions, positions)
		else:
			d = frappe.new_doc('Source Message')
			d.message = message
			d.context = context
		d.set('positions', positions)

		d.save(ignore_version=True, ignore_permissions=True)
		frappe.db.commit()


def get_postions_to_save(old_positions, new_positions):
	final_positions =  list(old_positions + new_positions)
	return final_positions

def get_formatted_messages(messages, app, app_version):
	message_map = frappe._dict({})

	# messages structure
	# [(position, source_text_1, context, line_no), (position, source_text_2)]
	for message_data in messages:
		if not message_data: continue
		position = message_data.get('position')
		message = message_data.get('source_text')
		context = message_data.get('context')
		line_no = message_data.get('line_no')
		position_dict = frappe._dict({
			'position': position,
			'line_no': line_no,
			'app': app,
			'app_version': app_version,
			'type': message_data.get('type'),
			'report': message_data.get('report'),
			'page': message_data.get('page'),
			'document_type': message_data.get('document_type'),
			'module': message_data.get('module')
		})
		if not message_map.get((message, context)):
			message_map[(message, context)] = [position_dict]
		else:
			message_map[(message, context)].append(position_dict)
	return message_map