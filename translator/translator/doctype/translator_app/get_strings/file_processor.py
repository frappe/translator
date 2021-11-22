import os
import re
import ast
import json
from typing import List, Tuple
import frappe
from frappe.exceptions import ValidationError
from frappe.model.utils import InvalidIncludePath, render_include
from frappe.utils import get_bench_path
from frappe.modules.import_file import read_doc_from_file

class C(ast.NodeVisitor):

	def __init__(self, path):
		self.path = path
		self.messages = []
		self.targets = ('label', 'role', 'options',
			'workflow_state_name', 'workflow_action_name',
			'item_label', 'item_type', 'description')
		super().__init__()

	def visit_Dict(self, node):
		for key, value in zip(node.keys, node.values):
			if isinstance(key, ast.Constant) and  isinstance(value, ast.Constant):
				if key.value in self.targets:
					self.messages.append(value.value)
		super().generic_visit( node)

	def visit_keyword(self, node):
		import ast

		if node.arg in self.targets:
			if isinstance(node.value, ast.Constant):
				self.messages.append(node.value.value)
		super().generic_visit( node)


class  FileProcessor():

	def __init__(self, path) -> None:
		self.path = path

	def get_messages(self):
		if (self.path.endswith(".js") or self.path.endswith(".html") or self.path.endswith('.vue') or self.path.endswith('.py')):
			return self.get_messages_from_file()
		# elif (self.path.endswith(".json")):
		# 	return self.get_messages_from_json()
		else:
			return []

	def get_messages_from_doc(self, doc):
		messages = []
		messages.extend([doc.get('label'), doc.get('description'), doc.get('name')])

		if doc.get('fields'):
			for field in doc.get('fields'):
				messages.extend([field.get('label'), field.get('description')])

				if field.get('fieldtype')=='Select' and field.get('options'):
					options = field.get('options').split('\n')
					if not "icon" in options[0]:
						messages.extend(options)
				if field.get('fieldtype')=='HTML' and field.get('options'):
					messages.append(field.get('options'))
		if doc.get('permissions'):
			for d in doc.get("permissions"):
				if d.get('role'):
					messages.append(d.get('role'))

		messages = [message for message in messages if message]
		messages = [(self.path, message) for message in messages if self.is_translatable(message)]

		messages = [
			{
				'position': os.path.join(self.path),
				'source_text': message[1],
				'context' : message[2] or '' if len(message) > 2 else '',
				'line_no' : message[3] or 0 if len(message) == 4 else 0,
			}
			for message in messages
		]
		return messages

	def get_messages_from_json(self):
		messages = []
		try:
			json_doc = read_doc_from_file(self.path)
		except IOError:
			return messages

		if type(json_doc) == type([]):
			[messages.extend(self.get_messages_from_doc(json.loads(doc))) for doc in json_doc]
		else:
			messages.extend(self.get_messages_from_doc(json_doc))

		return messages



	def get_messages_from_file(self) -> List[Tuple[str, str, str, str]]:
		"""Returns a list of transatable strings from a code file

		:param path: path of the code file
		"""

		if os.path.exists(self.path):
			with open(self.path, 'r') as sourcefile:
				try:
					file_contents = sourcefile.read()
				except Exception:
					print("Could not scan file for translation: {0}".format(self.path))
					return []

				return [
					{
						'position': self.path,
						'source_text': message,
						'context': context,
						'line_no': line
					}

					for (line, message, context) in self.extract_messages_from_code(file_contents)
				]
		else:
			return []

	def extract_messages_from_code(self, code):
		"""
			Extracts translatable strings from a code file
			:param code: code from which translatable files are to be extracted
			:param is_py: include messages in triple quotes e.g. `_('''message''')`
		"""
		from jinja2 import TemplateError

		try:
			code = frappe.as_unicode(render_include(code))

		# Exception will occur when it encounters John Resig's microtemplating code
		except (TemplateError, ImportError, InvalidIncludePath, IOError) as e:
			if isinstance(e, InvalidIncludePath):
				frappe.clear_last_message()

			pass

		messages = []
		pattern = r"_\(([\"']{,3})(?P<message>((?!\1).)*)\1(\s*,\s*context\s*=\s*([\"'])(?P<py_context>((?!\5).)*)\5)*(\s*,\s*(.)*?\s*(,\s*([\"'])(?P<js_context>((?!\11).)*)\11)*)*\)"

		for m in re.compile(pattern).finditer(code):
			message = m.group('message')
			context = m.group('py_context') or m.group('js_context')
			pos = m.start()

			if self.is_translatable(message):
				messages.append([pos, message, context])


		# india_setup = ast.parse(''.join(lines))
	
		messages = self.add_line_number(messages, code)
		if self.path.endswith('.py'):
			c = C(self.path)
			c.visit(ast.parse(code))
			messages.extend([[None,message, None] for message in c.messages])
		return messages

	def is_translatable(self, m):
		if re.search("[a-zA-Z]", m) and not m.startswith("fa fa-") and not m.endswith("px") and not m.startswith("eval:"):
			return True
		return False

	def add_line_number(self, messages, code):
		ret = []
		messages = sorted(messages, key=lambda x: x[0])
		newlines = [m.start() for m in re.compile(r'\n').finditer(code)]
		line = 1
		newline_i = 0
		for pos, message, context in messages:
			while newline_i < len(newlines) and pos > newlines[newline_i]:
				line+=1
				newline_i+= 1
			ret.append([line, message, context])
		return ret
