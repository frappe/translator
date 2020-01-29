from __future__ import unicode_literals
import frappe
from frappe.utils import get_fullname

def get_context(context):
	context.no_cache=True
	data = frappe.db.sql("""SELECT count(*) AS contribution_count, modified_by
		FROM `tabTranslated Message`
		WHERE modified_by != "Administrator"
		GROUP BY modified_by
		ORDER BY contribution_count
		DESC LIMIT 50
	""", as_dict=1)

	for d in data:
		d.fullname = get_fullname(d.modified_by)

	context.users = data
