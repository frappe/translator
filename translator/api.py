import frappe
import json
from frappe.utils import cint
from frappe.translate import load_lang, get_user_translations, get_messages_for_app

@frappe.whitelist(allow_guest=True)
def add_translations(translation_map, contributor_name, contributor_email, language):
	translation_map = json.loads(translation_map)
	for source_id, translation_dict in translation_map.items():
		translation_dict = frappe._dict(translation_dict)
		existing_doc_name = frappe.db.exists('Translated Message', {
			'source': source_id,
			'translation_type': 'Contribution',
			'context': translation_dict.context,
			'contributor_email': contributor_email
		})
		if existing_doc_name:
			frappe.set_value('Contributed Translation', existing_doc_name, 'target_name', translation_dict.translated_text)
		else:
			doc = frappe.get_doc({
				'doctype': 'Translated Message',
				'source': source_id,
				'translation_type': 'Contribution',
				'contribution_status': 'Pending',
				'translated': translation_dict.translated_text,
				'context': translation_dict.context,
				'contributor_email': contributor_email,
				'contributor_name': contributor_name,
				'language': language
			})
			doc.insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def get_strings_for_translation(language, start=0, page_length=1000, search_text=''):

	start = cint(start)
	page_length = cint(page_length)

	apps = [d.name for d in frappe.get_all('Translator App')]

	messages = []
	translated_message_dict = load_lang(lang=language)
	contributed_translations = get_contributed_translations(language)

	app_messages = frappe.cache().get_value('app_messages') or []
	if not app_messages:
		# getting as_list to save cache space
		app_messages = frappe.get_all('Source Message',
			fields=['position', 'message', 'context', 'line_no', 'name'],
			filters={
				'app': ['in', apps],
			}, as_list=1)

		frappe.cache().set_value('app_messages', app_messages)

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
			'id': message[4],
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

	doc_list = frappe.get_all('Translated Message',
		fields=['source', 'translated', 'contribution_status', 'creation',
			'language', 'contributor_email', 'contributor_name', 'modified_by'],
		filters={
			'language': language,
			'contribution_status': ['!=', 'Rejected'],
			'translation_type': 'Contribution',
		})

	doc_map = {}
	for doc in doc_list:
		if doc_map.get(doc.source_string):
			doc_map[doc.source_string].append(doc)
		else:
			doc_map[doc.source_string] = [doc]

	frappe.cache().hset('contributed_translations', language, doc_map)

	return doc_map