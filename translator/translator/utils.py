import frappe
from frappe.translate import load_lang, get_user_translations, get_messages_for_app
from frappe.utils import cint


@frappe.whitelist(allow_guest=True)
def get_strings_for_translation(language, start=0, page_length=1000, search_text=''):

	start = cint(start)
	page_length = cint(page_length)

	apps = frappe.get_all_apps(True)

	messages = []
	translated_message_dict = load_lang(lang=language)
	contributed_translations = get_contributed_translations(language)

	app_messages = frappe.cache().hget('app_messages', language) or []
	if not app_messages:
		for app in apps:
			app_messages += get_messages_for_app(app)

		frappe.cache().hset('app_messages', language, app_messages)

	for message in app_messages:
		path_or_doctype = message[0] or ''
		source_text = message[1]
		line = None
		context = None

		if len(message) > 2:
			context = message[2]
			line = message[3]

		doctype = path_or_doctype.rsplit('DocType: ')[1] if path_or_doctype.startswith('DocType:') else None

		source_key = source_text
		if context:
			source_key += ':' + context

		translated_text = translated_message_dict.get(source_key)

		messages.append(frappe._dict({
			'id': source_text,
			'source_text': source_text,
			'translated_text': translated_text or '',
			'user_translated': bool(False),
			'context': context,
			'line': line,
			'path': path_or_doctype if not doctype else None,
			'doctype': doctype,
			'contributions': contributed_translations.get(source_text) or []
		}))

	frappe.clear_messages()

	if search_text:
		messages = [message for message in messages if search_text in message.source_text]

	messages = sorted(messages, key=lambda x: x.translated_text, reverse=False)

	return messages[start:start + page_length]

def get_contributed_translations(language):
	cached_records = frappe.cache().hget('contributed_translations', language)
	if cached_records:
		return cached_records

	doc_list = frappe.get_all('Contributed Translation',
		fields=['source_string', 'translated_string', 'status', 'creation',
			'language', 'contributor_email', 'contributor_name', 'modified_by'],
		filters={
			'language': language,
			'status': ['!=', 'Rejected'],
		}, order_by='verified')

	doc_map = {}
	for doc in doc_list:
		if doc_map.get(doc.source_string):
			doc_map[doc.source_string].append(doc)
		else:
			doc_map[doc.source_string] = [doc]

	frappe.cache().hset('contributed_translations', language, doc_map)

	return doc_map