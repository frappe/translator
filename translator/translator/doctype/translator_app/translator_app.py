# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals, with_statement
import requests
import frappe
import os
import tarfile
from frappe.model.document import Document
from frappe.utils import  get_site_path, random_string
from frappe.utils import update_progress_bar
from frappe.core.utils import find

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

			formatted_messages = get_formatted_messages(messages, self.app_name, source.source)
			import_source_messages(formatted_messages, self.name)

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



def import_source_messages(message_map, name):
	"""Import messages from apps listed in **Translator App** as **Source Message**"""
	l = len(message_map)
	# frappe.db.set_value('Translator App', name, 'log', message_map)

	frappe.db.sql("UPDATE `tabSource Message` SET `disabled`=1")
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
		# except:
		# 	pass
				# log = str(frappe.db.get_value('Translator App', name, 'log')) + str(message) + context
				# frappe.db.set_value('Translator App', name, 'log', log)

		update_progress_bar("Importing messages", i, l)

def get_postions_to_save(old_positions, new_positions):
	final_positions = []
	for row in new_positions:
		old_row = find(old_positions, lambda d: d.position == row['position'])
		if old_row:
			old_row.update(row)
			final_positions.append(old_row)
			old_positions.remove(old_row)
		else:
			final_positions.append(row)
	return final_positions

def get_formatted_messages(messages, app, app_version):
	message_map = frappe._dict({})

		# messages structure
		# [(position, source_text_1, context, line_no), (position, source_text_2)]
	for message_data in messages:
		if not message_data: continue
		position = message_data[0]
		message = message_data[1]
		context = message_data[2] or '' if len(message_data) > 2 else ''
		line_no = message_data[3] or 0 if len(message_data) == 4 else 0
		position_dict = frappe._dict({
			'position': position,
			'line_no': line_no,
			'app': app,
			'app_version': app_version
		})
		if not message_map.get((message, context)):
			message_map[(message, context)] = [position_dict]
		else:
			message_map[(message, context)].append(position_dict)
	return message_map