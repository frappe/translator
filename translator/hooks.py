app_name = "translator"
app_title = "Translator"
app_publisher = "Frappe Technologies"
app_description = "Translation Portal for Frappe Apps"
app_icon = "icon-comment"
app_color = "green"
app_email = "info@frappe.io"
app_url = "https://frappe.io"
app_version = "0.0.1"

clear_cache = "translator.helpers.clear_cache"

fixtures = ["Custom Field"]

website_context = {
	"brand_html": "<img class='navbar-icon' src='/assets/translator/img/erp-icon.svg' />ERPNext Translator",
	"top_bar_items": [
		{"label": "Hall of Fame", "url": "/hall-of-fame", "right": 1},
		{"label": "Help", "url": "/help", "right": 1}
	],
	"favicon": "/assets/translator/img/favicon.ico",
}

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/translator/css/translator.css"
# app_include_js = "/assets/translator/js/translator.js"

# include js, css files in header of web template
web_include_css = [
	"/assets/translator/css/custom.css",
	"/assets/translator/css/ion-rangeslider/ion.rangeSlider.css",
	"/assets/translator/css/ion-rangeslider/ion.rangeSlider.skinFlat.css"
]
web_include_js = [
	"/assets/translator/js/translator.js",
	"/assets/translator/js/ion.rangeSlider.min.js"
]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "translator.install.before_install"
# after_install = "translator.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "translator.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"translator.tasks.all"
# 	],
# 	"daily": [
# 		"translator.tasks.daily"
# 	],
	"hourly": [
		"translator.data.write_csv_for_all_languages",
		"translator.translator.doctype.contributed_translation.contributed_translation.spush_contributions_to_respected_versions"
	],
	# "weekly": [
	# 	"translator.helpers.weekly_updates"
	# ]
	"monthly": [
		"translator.helpers.monthly_updates"
	]
}

get_website_user_home_page = "translator.helpers.get_home_page"

# Testing
# -------

# before_tests = "translator.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "translator.event.get_events"
# }
