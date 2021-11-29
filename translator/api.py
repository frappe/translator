import frappe
import json
from frappe.utils import cint
from frappe.translate import load_lang, get_user_translations, get_messages_for_app

@frappe.whitelist(allow_guest=True)
def add_translations(translation_map, contributor_name, contributor_email, language):
	translation_map = json.loads(translation_map)
	name_map = frappe._dict({})
	for source_id, translation_dict in translation_map.items():
		translation_dict = frappe._dict(translation_dict)
		existing_doc = frappe.db.get_all('Translated Message', {
			'source': source_id,
			'translation_source': 'Community Contribution',
			'contributor_email': contributor_email
		})
		if existing_doc:
			existing_doc_name = existing_doc[0].name
			name_map[translation_dict.name] = existing_doc_name
			frappe.db.set_value('Translated Message', existing_doc_name, 'translated', translation_dict.translated_text)
		else:
			doc = frappe.get_doc({
				'doctype': 'Translated Message',
				'source': source_id,
				'translation_source': 'Community Contribution',
				'contribution_status': 'Pending',
				'translated': translation_dict.translated_text,
				'contributor_email': contributor_email,
				'contributor_name': contributor_name,
				'language': language
			})
			doc.insert(ignore_permissions=True)
			name_map[translation_dict.name] = doc.name

	frappe.db.commit()

	return name_map


@frappe.whitelist(allow_guest=True)
def get_strings_for_translation(language, start=0, page_length=100, search_text='', app_name='Wiki'):
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
						AND (translated.contribution_status='Verified' OR translated.translation_source != 'Community Contribution')
					)
				Inner join `tabSource Message Position` as smp
					on (
						source.name=smp.parent
					)
			WHERE
				source.disabled != 1 && ((source.message like %(search_text)s or translated.translated like %(search_text)s) and smp.app=%(app_name)s)
			ORDER BY
				translated_by_google
		) as res
		GROUP BY res.id
		ORDER BY  res.translated, res.translated_by_google, res.creation
		LIMIT %(page_length)s
		OFFSET %(start)s
	""", dict(language=language, search_text='%' + search_text + '%', page_length=cint(page_length), start=cint(start), app_name=app_name), as_dict=1 )

@frappe.whitelist(allow_guest=True)
def get_source_additional_info(source, language=''):
	data = {}
	data['contributions'] = frappe.get_all('Translated Message', filters={
		'translation_source': 'Community Contribution',
		'source': source,
		'language': language
	}, fields=['name', 'translated', 'contributor_email', 'contributor_name', 'creation', 'contribution_status', 'modified_by'])

	data['positions'] = frappe.get_all('Source Message Position', filters={
		'parent': source,
	}, fields=['position as path', 'line_no', 'app', 'app_version'])

	return data

@frappe.whitelist(allow_guest=True)
def upvote_translation(translation_id, user_email, site):
	# translation votes
	pass

@frappe.whitelist(allow_guest=True)
def get_contribution_status(translation_id, user_email=None, site=None):
	return frappe.get_doc('Translated Message', translation_id)
