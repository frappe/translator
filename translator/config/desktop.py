from frappe import _

def get_data():
	return [
		{
			"module_name": "Translation",
			"category": "Modules",
			"label": _("Verify Translations"),
			"color": "#4c927e",
			"reverse": 1,
			"icon": "octicon octicon-tasklist",
			"type": "module",
			"description": "Verify Contributed Translations."
		}
	]
