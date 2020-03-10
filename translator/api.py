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
			'translation_source': 'Community Contribution',
			'context': translation_dict.context,
			'contributor_email': contributor_email
		})
		if existing_doc_name:
			frappe.set_value('Contributed Translation', existing_doc_name, 'target_name', translation_dict.translated_text)
		else:
			doc = frappe.get_doc({
				'doctype': 'Translated Message',
				'source': source_id,
				'translation_source': 'Community Contribution',
				'contribution_status': 'Pending',
				'translated': translation_dict.translated_text,
				'context': translation_dict.context,
				'contributor_email': contributor_email,
				'contributor_name': contributor_name,
				'language': language
			})
			doc.insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def get_strings_for_translation(language, start=0, page_length=100, search_text=''):
	return frappe.db.sql("""
		SELECT * FROM (
			SELECT
				DISTINCT source.name AS id,
				source.message AS source_text,
				source.context AS context,
				translated.translated AS translated_text,
				CASE WHEN translated.translated IS NOT NULL THEN 1 ELSE 0 END AS translated,
				CASE WHEN translated.translation_source = 'Google Translated' THEN 1 ELSE 0 END AS translated_by_google,
				translated.contributor_name,
				translated.contributor_email,
				translated.modified_by,
				source.creation
			FROM `tabSource Message` source
				LEFT JOIN `tabTranslated Message` AS translated
					ON (
						source.name=translated.source
						AND translated.language = %(language)s
						AND (translated.contribution_status='Verified' OR translated.translation_source = 'Google Translated')
					)
			WHERE
				source.disabled != 1 && (source.message like %(search_text)s or translated.translated like %(search_text)s)
			ORDER BY
				translated_by_google
		) as res
		GROUP BY res.id
		ORDER BY  res.translated, res.translated_by_google, res.creation
		LIMIT %(page_length)s
		OFFSET %(start)s
	""", dict(language=language, search_text='%' + search_text + '%', page_length=cint(page_length), start=cint(start)), as_dict=1)

@frappe.whitelist(allow_guest=True)
def get_contributions(source, language=''):
	return frappe.get_all('Translated Message', filters={
		'translation_source': 'Community Contribution',
		'source': source,
		'language': language
	}, fields=['translated', 'contributor_email', 'contributor_name', 'creation', 'contribution_status', 'modified_by'])