# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, absolute_import
import frappe, os

from frappe.translate import read_csv_file, get_all_languages, write_translations_file, get_messages_for_app
from translator.translator.doctype.translated_message.translated_message import get_placeholders_count
import frappe.utils
from frappe.utils import strip, update_progress_bar
from frappe import safe_decode
import json
from csv import writer
import csv
import frappe.exceptions
from six import iteritems


def import_source_messages():
	"""Import messages from apps listed in **Translator App** as **Source Message**"""
	frappe.db.sql("UPDATE `tabSource Message` SET `disabled`=1")
	for app in frappe.db.sql_list("select name from `tabTranslator App`"):
		app_version = frappe.get_hooks(app_name='frappe')['app_version'][0]
		messages = get_messages_for_app(app)
		# messages structure
		# [(position, source_text_1, context), (position, source_text_2)]

		for message in messages:
			context = ''
			if len(message) > 2 and message[2]:
				context = message[2]

			source_message = frappe.db.get_all('Source Message', {
				'message': message[1],
				'context': context,
				'app': app,
			}, ['name', 'message', 'position', 'app_version', 'context'], limit=1)

			source_message = source_message[0] if source_message else None
			if source_message:
				d = frappe.get_doc("Source Message", source_message['name'])
				if source_message["position"] != message[0]:
					d.position = message[0]
				if source_message['app_version'] != app_version:
					d.app_version = app_version
				d.disabled = 0
			else:
				d = frappe.new_doc('Source Message')
				d.position = message[0]
				d.message = message[1]
				d.app = app
				d.context = context
				d.app_version = app_version
			d.save()

def get_untranslated(lang):
	return frappe.db.sql("""
		SELECT
			source.name,
			source.message
		FROM `tabSource Message` source
			LEFT JOIN `tabTranslated Message` translated
				ON (source.name=translated.source AND translated.language = %s)
		WHERE translated.name IS NULL AND source.disabled != 1
	""", (lang, ))

def write_csv_for_all_languages():
	langs = frappe.db.sql_list("select name from tabLanguage")
	apps = frappe.db.sql_list("select name from `tabTranslator App`")
	for lang in langs:
		for app in apps:
			print("Writing for {0}-{1}".format(app, lang))
			path = os.path.join(frappe.get_app_path(app, "translations", lang + ".csv"))
			write_csv(app, lang, path)

def write_csv(app, lang, path):
	translations = get_translations_for_export(app, lang)

	parent = None
	parent_dict = {}
	if '-' in lang:
		# get translation from parent
		# for example es and es-GT
		parent = lang.split('-')[0]
		parent_dict = {}
		for t in get_translations_for_export(app, parent):
			parent_dict[t[1]] = t[2]

	with open(path, 'w') as msgfile:
		w = writer(msgfile, lineterminator='\n')
		for t in translations:
			# only write if translation is different from parent
			if (not parent) or (t[2] != parent_dict.get(t[1])):
				if t[2]:
					print(t[2])
				w.writerow([t[0] if t[0] else '', t[1], strip(t[2] or '')])
				# w.writerow([t[0].encode('utf-8') if t[0] else '', t[1].encode('utf-8'), strip(t[2] or '').encode('utf-8')])

def get_translations_for_export(app, lang):
	# should return all translated text
	return frappe.db.sql("""
		SELECT
			source.position,
			source.message,
			COALESCE(contributed.translated_string, translated.translated) AS translated_text,
			contributed.context
		FROM `tabSource Message` source
			LEFT JOIN `tabTranslated Message` translated
				ON (source.name=translated.source AND translated.language = %(language)s)
			LEFT JOIN `tabContributed Translation` contributed
				ON (
					source.message=contributed.source_string
					AND contributed.language = %(language)s
					AND contributed.status = 'Verified'
					AND ((contributed.context IS NULL and contributed.context IS NULL) OR contributed.context=source.context)
				)
		WHERE
			source.disabled != 1 AND source.app = %(app)s
		GROUP BY
			source.message, source.context
		HAVING translated_text IS NOT NULL
		ORDER BY
			translated_text DESC
	""", dict(language=lang, app=app))

def export_untranslated_to_json(lang, path):
	ret = {}
	for name, message in get_untranslated(lang):
		ret[name] = {
			"message": message.replace('$', '$$')
		}
	with open(path, 'wb') as f:
		json.dump(ret, f, indent=1)


def copy_translations(from_lang, to_lang):
	translations = frappe.db.sql("""select source, translated from `tabTranslated Message` where language=%s""", (from_lang, ))
	l = len(translations)
	for i, d in enumerate(translations):
		source, translated = d
		if not frappe.db.get_value('Translated Message', {"source": source, "language": to_lang}):
			t = frappe.new_doc('Translated Message')
			t.language = to_lang
			t.source = source
			t.translated = translated
			try:
				t.save()
			except frappe.ValidationError:
				pass

		update_progress_bar("Copying {0} to {1}".format(from_lang, to_lang), i, l)

def read_translation_csv_file(path):
	with open(path, 'rt') as f:
		reader = unicode_csv_reader(f)
		return list(reader)

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield [safe_decode(cell, 'utf-8') for cell in row]


def import_translations_from_csv(lang, path, modified_by='Administrator', if_older_than=None):
	content = read_translation_csv_file(path)
	if len(content[0]) == 2:
		content = [c for c in content if len(c) == 2]
		content = [('', c[0], c[1]) for c in content]
	count = 0
	print('importing', len(content), 'translations')
	for pos, source_message, translated in content:

		source_name = frappe.db.get_value("Source Message", {"message": source_message})

		if not source_name:
			continue

		source = frappe.get_doc('Source Message', source_name)

		if source.disabled:
			continue
		dest = frappe.db.get_value("Translated Message", {"source": source_name, "language": lang})
		if dest:
			d = frappe.get_doc('Translated Message', dest)
			if if_older_than and d.modified > if_older_than:
				continue

			if d.modified_by != "Administrator" or d.translated != translated:
				frappe.db.set_value("Translated Message", dest, "translated", translated, modified_by=modified_by)
				count += 1
		else:
			dest = frappe.new_doc("Translated Message")
			dest.language = lang
			dest.translated = translated
			dest.source = source.name
			dest.save()
			count += 1
	print('updated', count)


def get_translation_from_google(lang, message):
	if lang == "cz":
		lang = "cs"
	s = frappe.utils.get_request_session()
	resp = s.get("https://www.googleapis.com/language/translate/v2", params={
		"key": frappe.conf.google_api_key,
		"source": "en",
		"target": lang,
		"q": message
	})
	resp.raise_for_status()
	return resp.json()["data"]["translations"][0]["translatedText"]

def translate_untranslated_from_google(lang):
	if lang == "en":
		return

	if lang=='zh-cn': lang = 'zh'
	if lang=='zh-tw': lang = 'zh-TW'

	if not get_lang_name(lang):
		print('{0} not supported by Google Translate'.format(lang))
		return

	count = 0
	untranslated = get_untranslated(lang)
	l = len(untranslated)

	for i, d in enumerate(untranslated):
		source, message = d
		if not frappe.db.get_value('Translated Message', {"source": source, "language": lang}):
			t = frappe.new_doc('Translated Message')
			t.language = lang
			t.source = source
			t.translated = get_translation_from_google(lang, message)
			try:
				t.save()
			except frappe.exceptions.ValidationError:
				continue
			count += 1
			frappe.db.commit()

		update_progress_bar("Translating {0}".format(lang), i, l)

	print(lang, count, 'imported')


def get_lang_name(lang):
	s = frappe.utils.get_request_session()
	resp = s.get("https://www.googleapis.com/language/translate/v2/languages", params={
		"key": frappe.conf.google_api_key,
		"target": "en"
	})

	languages = resp.json()['data']['languages']
	for l in languages:
		if l['language'] == lang:
			return l['name']

	return None