from __future__ import unicode_literals
import frappe

def get_info(lang, this_month = False):
	def _get():
		condition = ""
		if this_month:
			condition = " and modified > DATE_SUB(NOW(), INTERVAL 1 MONTH)"

		return {
			"total": frappe.db.sql("""select count(*) from `tabSource Message`
				where disabled != 1""")[0][0],
			"verified": frappe.db.sql("""select count(*) from `tabTranslated Message`
				where language=%s and verified > 0 {0}""".format(condition), lang)[0][0],
			"edited": frappe.db.sql("""select count(*) from `tabTranslated Message`
				where language=%s and modified_by != 'Administrator' {0}""".format(condition),
					lang)[0][0]
		}

	if this_month:
		return _get()
	else:
		return frappe.cache().get_value("lang-data:" + lang, _get)

@frappe.whitelist()
def verify(message):
	frappe.get_doc({
		"doctype": "Translated Message Validation",
		"message": message
	}).insert(ignore_permissions=1)

@frappe.whitelist()
def update(message, source, translated, language):
	if message:
		message = frappe.get_doc("Translated Message", message)
		message.translated = translated
		message.save(ignore_permissions=1)
	elif source:
		message = frappe.new_doc("Translated Message")
		message.translated = translated
		message.language = language
		message.source = source
		message.save(ignore_permissions=1)
	else:
		raise frappe.ValidationError("Message not found")

@frappe.whitelist()
def report(message, value):
	message = frappe.get_doc("Source Message", message)
	message.flagged = value
	message.save(ignore_permissions=1)

def monthly_updates():
	translators = frappe.db.sql_list("""select distinct modified_by from
		`tabTranslated Message`""")

	message = frappe.get_template("/templates/emails/translator_update.md").render({
		"frappe": frappe
	})

	# refer unsubscribe against the administrator
	# document for test
	frappe.sendmail(translators, "ERPNext Translator <hello@erpnext.com>",
		"Montly Update", message, bulk=True, reference_doctype="User",
		reference_name="Administrator")
