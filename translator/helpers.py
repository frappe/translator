from __future__ import unicode_literals

import frappe
from frappe.utils import validate_email_address


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
	updated = False
	if message:
		message = frappe.get_doc("Translated Message", message)
		if message.language == language:
			message.translated = translated
			message.save(ignore_permissions=1)
			updated = True

	if not updated:
		message = frappe.new_doc("Translated Message")
		message.translated = translated
		message.language = language
		message.source = source
		message.save(ignore_permissions=1)

@frappe.whitelist()
def report(message, value):
	message = frappe.get_doc("Source Message", message)
	message.flagged = value
	message.save(ignore_permissions=1)

def monthly_updates():
	translators = frappe.db.sql_list("select DISTINCT(contributor) from `tabContributed Translation`")
	translators = [email for email in translators if validate_email_address(email)]

	message = frappe.get_template("/templates/emails/translator_update.md").render({
		"frappe": frappe
	})

	# refer unsubscribe against the administrator
	# document for test
	frappe.sendmail(
		recipients=translators,
		sender="ERPNext Translator <hello@erpnext.com>",
		subject="Monthly Update",
		message=message,
		reference_doctype="User",
		reference_name="Administrator"
	)

def clear_cache():
	for lang in frappe.db.sql_list("select name from tabLanguage"):
		frappe.cache().delete_value("lang-data:" + lang)

def get_home_page(user):
	""" website user should be redirected to /index after login"""
	return "/index"
