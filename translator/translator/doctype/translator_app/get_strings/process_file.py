import os
import re
from typing import List, Tuple
import frappe
from frappe.model.utils import InvalidIncludePath, render_include
from frappe.utils import get_bench_path

class ProcessFile():

	def __init__(self, path) -> None:
		self.path = path

	def get_messages(self):
		if not (self.path.endswith(".js") or self.path.endswith(".html") or self.path.endswith('.vue')):
			return []
		return self.get_messages_from_file()

	def get_messages_from_file(self) -> List[Tuple[str, str, str, str]]:
		"""Returns a list of transatable strings from a code file

		:param path: path of the code file
		"""
		frappe.flags.setdefault('scanned_files', [])
		# TODO: Find better alternative
		# To avoid duplicate scan
		if self.path in set(frappe.flags.scanned_files):
			return []

		frappe.flags.scanned_files.append(self.path)

		bench_path = get_bench_path()
		if os.path.exists(self.path):
			with open(self.path, 'r') as sourcefile:
				try:
					file_contents = sourcefile.read()
					print(file_contents)
				except Exception:
					print("Could not scan file for translation: {0}".format(self.path))
					return []

				return [
					(self.path, message, context, line)
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

		return self.add_line_number(messages, code)

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
