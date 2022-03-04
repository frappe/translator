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
web_include_css = [
	"/assets/translator/css/custom.css",
]


doc_events = {
	"User": {
		"after_insert": "translator.utils.set_default_role"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"Weekly Long": [
		"translator.translator.doctype.translator_app.translator_app.extract_strings_weekly",
		"translator.translator.doctype.translator_app.translator_app.create_release_weekly",
		"translator.translator.doctype.translator_app.translator_app.translate_from_google",
	]
}
