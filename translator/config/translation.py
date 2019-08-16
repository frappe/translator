from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Translations"),
			"items": [
				{
					"type": "doctype",
					"name": "Contributed Translation"
				}
			]
		}

	]
