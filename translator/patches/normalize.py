import frappe
import click
from translator.data import import_source_messages
from frappe.core.page.data_import_tool.data_import_tool import import_file_by_path
from translator.data import import_translated_from_text_files

def execute():
	frappe.db.auto_commit_on_many_writes = False
	# reload doc Source message
	frappe.reload_doc("translator", "doctype", "source_message")
	frappe.reload_doc("translator", "doctype", "translator_app")

	frappe.delete_doc('Page', 'website-home')
	frappe.delete_doc('Page', 'user-properties')
	frappe.delete_doc('Page', 'Setup')
	frappe.get_doc({'doctype': 'Translator App', 'app_name': 'frappe'}).save()
	frappe.get_doc({'doctype': 'Translator App', 'app_name': 'erpnext'}).save()
	# import_source_messages()
	import_file_by_path('source_messages.csv')
	frappe.db.commit()

	count = frappe.db.count("Translated Message")

	source_messages = dict(frappe.db.sql("select message, name from `tabSource Message`"))
	for name, source, modified, modified_by in frappe.db.sql("select name, source, modified, modified_by from `tabTranslated Message`"):
		if source in source_messages:
			frappe.db.set_value("Translated Message", name, "source", source_messages[source], modified_by=modified_by, modified=modified)
		else:
			d = frappe.new_doc("Source Message")
			d.disabled = 1
			d.message = source
			d.save()
			source_messages[source] = d.name
			frappe.db.set_value("Translated Message", name, "source", d.name, modified_by=modified_by, modified=modified)
		count -= 1
		click.clear()
		print(count, 'remaining')

	frappe.db.commit()

	import_translated_from_text_files('../uts', '../ts')
	frappe.db.commit()

	# reload doc Translated Message
	frappe.db.auto_commit_on_many_writes = True

