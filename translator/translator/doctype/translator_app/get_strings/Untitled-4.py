path = "/Users/mohammadhasnainrajan/frappe/erpnext-v13/apps/erpnext/erpnext/regional/india/setup.py"
# path = '/Users/mohammadhasnainrajan/frappe/erpnext-v13/apps/frappe/frappe/core/page/permission_manager/permission_manager.py'
with open(path) as fp:
	lines = fp.readlines()
india_setup = ast.parse("".join(lines))


class C(ast.NodeVisitor):
	def __init__(self):
		self.messages = []
		super().__init__()

	def visit_dict(self, node):
		print(node)
		super().generic_visit(node)

	def visit_keyword(self, node):
		import ast

		if node.arg in ("label", "role"):

			# print(node.value.__dict__)
			# print(type(node.value))
			# print(isinstance(node.value, ast.Constant))
			# print(type(node.value))
			self.messages.append(node.value.value)
		#  print(node.value.value)

		super().generic_visit(node)


c = C()
c.visit(india_setup)
# print(c.messages)
