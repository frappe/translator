# Copyright (c) 2021, Frappe Technologies and Contributors
# See license.txt

import frappe
import os
import csv
import unittest
from frappe.core.doctype.file.file import File
from translator.translator.doctype.translator_app.get_strings.app_processor import AppProcessor
from translator.translator.doctype.translator_app.get_strings.doctype_processor import DoctypeProcessor
from translator.translator.doctype.translator_app.get_strings.module_processor import ModuleProcessor
from translator.translator.doctype.translator_app.get_strings.report_processor import ReportProcessor
from translator.translator.doctype.translator_app.get_strings.page_processor import PageProcessor
from translator.translator.doctype.translator_app.get_strings.folder_processor import FolderProcessor
from translator.translator.doctype.translator_app.get_strings.folder_processor import FileProcessor

class TestExtractStringsJob(unittest.TestCase):
	def test_app_processor(self):
		self.maxDiff = None
		messages = AppProcessor(get_app_path(), 'Healthcare').get_messages()

		# for message_data in messages:
		# 	if not message_data:
		# 		continue
		# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

		# 	keys = ["position", "source_text", "context",  "module", "type", "document_name" ]

		# 	for key in keys:
		# 		val = message_data.get(key)
		# 		message_data[key] = str(val) if val else ''
		# 	val = message_data.get('line_no')
		# 	message_data['line_no'] = str(val) if val else '0'

		process_extracted_messages(messages)

		messages_target = read_csv(get_result_path('app_result.csv'))

		process_stored_messages(messages_target)

		# for message_data in messages_target:
		# 	if message_data.get('source_text') == 'False':
		# 		message_data['source_text'] = ''

		self.assertCountEqual(messages, messages_target)

	def test_module_processor(self):
		self.maxDiff = None
		messages = ModuleProcessor(get_module_path(), 'Healthcare').get_messages()
		process_extracted_messages(messages)
		messages_target = read_csv(get_result_path('module_result.csv'))
		process_stored_messages(messages_target)
		self.assertCountEqual(messages, messages_target)

	def test_doctype_processor(self):
		self.maxDiff = None
		messages = DoctypeProcessor(get_doctype_path(), 'Patient Appointment').get_messages()
		process_extracted_messages(messages)
		messages_target = read_csv(get_result_path('doctype_result.csv'))
		process_stored_messages(messages_target)
		self.assertCountEqual(messages, messages_target)

	def test_report_processor(self):
		self.maxDiff = None
		messages = ReportProcessor(get_report_path(), 'Patient Appointment Analytics').get_messages()
		process_extracted_messages(messages)
		messages_target = read_csv(get_result_path('report_result.csv'))
		process_stored_messages(messages_target)
		self.assertCountEqual(messages, messages_target)

	def test_page_processor(self):
		self.maxDiff = None
		messages = PageProcessor(get_page_path(), 'Patient Progress').get_messages()
		process_extracted_messages(messages)
		messages_target = read_csv(get_result_path('page_result.csv'))
		process_stored_messages(messages_target)
		self.assertCountEqual(messages, messages_target)

	def test_folder_processor(self):
		self.maxDiff = None
		messages = FolderProcessor(get_folder_path()).get_messages()
		process_extracted_messages(messages)
		messages_target = read_csv(get_result_path('folder_result.csv'))
		process_stored_messages(messages_target)
		self.assertCountEqual(messages, messages_target)

	def test_file_processor(self):
		self.maxDiff = None
		messages = FileProcessor(get_file_path()).get_messages()
		process_extracted_messages(messages)
		messages_target = read_csv(get_result_path('file_result.csv'))
		process_stored_messages(messages_target)
		self.assertCountEqual(messages, messages_target)

def process_extracted_messages(messages, file=False):
	for message_data in messages:
		if not message_data:
			continue
		message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

		keys = ["position", "source_text", "context",  "module", "type", "document_name" ]

		for key in keys:
			val = message_data.get(key)
			message_data[key] = str(val) if val else ''

		val = message_data.get('line_no')
		message_data['line_no'] = str(val) if val else '0'

def process_stored_messages(messages):
	for message_data in messages:
		if message_data.get('source_text') == 'False':
			message_data['source_text'] = ''

def get_result_path(name):
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', name)


def get_app_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare')

def get_module_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare', 'healthcare')

def get_doctype_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare', 'healthcare', 'healthcare', 'doctype')

def get_report_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare', 'healthcare', 'healthcare', 'report')

def get_page_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare', 'healthcare', 'healthcare', 'page')

def get_folder_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare', 'healthcare', 'healthcare', 'web_form')

def get_file_path():
	return frappe.get_app_path('translator', 'translator', 'doctype',
		'extract_strings_job', 'fixtures', 'healthcare', 'healthcare', 'healthcare', 'setup.py')


# out_file = open(get_result_path(), "w")


def read_csv(filename):
    with open(filename) as f:
        file_data=csv.reader(f)
        headers=next(file_data)
        return [dict(zip(headers,i)) for i in file_data]



# Use the following code to generate fixtures for app

# import csv
# from translator.translator.doctype.translator_app.get_strings.app_processor import AppProcessor
# a_file = open(get_result_path('app_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = AppProcessor(get_app_path(), 'Healthcare').get_messages()
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()


# Use the following code to generate fixtures for module

# import csv
# from translator.translator.doctype.translator_app.get_strings.module_processor import ModuleProcessor
# a_file = open(get_result_path('module_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = ModuleProcessor(get_module_path(), 'Healthcare').get_messages()
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()


# Use the following code to generate fixtures for doctype

# import csv
# from translator.translator.doctype.translator_app.get_strings.doctype_processor import DoctypeProcessor
# a_file = open(get_result_path('doctype_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = DoctypeProcessor(get_doctype_path(), 'Patient Appointment').get_messages()
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()


# Use the following code to generate fixtures for report

# import csv
# from translator.translator.doctype.translator_app.get_strings.report_processor import ReportProcessor
# a_file = open(get_result_path('report_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = ReportProcessor(get_report_path(), 'Patient Appointment Analytics').get_messages()
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()



# Use the following code to generate fixtures for page

# import csv
# from translator.translator.doctype.translator_app.get_strings.page_processor import PageProcessor
# a_file = open(get_result_path('page_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = PageProcessor(get_page_path(), 'Patient Progress').get_messages()
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()


# Use the following code to generate fixtures for folder

# import csv
# from translator.translator.doctype.translator_app.get_strings.folder_processor import FolderProcessor
# a_file = open(get_result_path('folder_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = FolderProcessor(get_folder_path()).get_messages()
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()



# Use the following code to generate fixtures for file

# import csv
# from translator.translator.doctype.translator_app.get_strings.file_processor import FileProcessor
# a_file = open(get_result_path('file_result.csv'), "w")

# keys = ["position",
# 	"source_text",
# 	"context",
# 	"line_no",
# 	"module",
# 	"type",
# 	"document_name"
# ]

# dict_writer = csv.DictWriter(a_file, keys)
# dict_writer.writeheader()
# messages = FileProcessor(get_file_path()).get_messages()
# process_extracted_messages(messages)
# for message_data in messages:
# 	if not message_data:
# 		continue
# 	message_data["position"]=os.path.relpath(message_data.get("position"), os.getcwd())

# dict_writer.writerows(messages)
# a_file.close()