# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, absolute_import
import frappe, os

from frappe.translate import read_csv_file, get_all_languages, write_translations_file, get_messages_for_app
from translator.translator.doctype.translated_message.translated_message import get_placeholders_count
import frappe.utils
from frappe.utils import strip, update_progress_bar
import json
from csv import writer
import csv
import frappe.exceptions
from six import iteritems

def import_languages():
	with open(frappe.get_app_path("frappe", "data", "languages.txt"), "r") as f:
		for l in unicode(f.read(), "utf-8").splitlines():
			if l:
				code, name = l.strip().split(None, 1)
				if not frappe.db.exists("Language", code):
					print("inserting " + code)
					frappe.get_doc({
						"doctype":"Language",
						"language_code": code,
						"language_name": name
					}).insert()

		frappe.db.commit()

def import_translations():
	apps_path = frappe.get_app_path("frappe", "..", "..")
	for app in os.listdir(apps_path):
		translations_folder = os.path.join(apps_path, app, app, "translations")
		if os.path.exists(translations_folder):
			for lang in frappe.db.sql_list("select name from tabLanguage"):
				path = os.path.join(translations_folder, lang + ".csv")
				if os.path.exists(path):
					print("Evaluating {0}...".format(lang))
					data = read_csv_file(path)
					for m in data:
						if not frappe.db.get_value("Translated Message",
							{"language": lang, "source": m[0]}):
							frappe.get_doc({
								"doctype": "Translated Message",
								"language": lang,
								"source": m[0],
								"translated": m[1],
								"verfied": 0
							}).insert()
							frappe.db.commit()
				else:
					print(path + " does not exist")


def export_translations():
	# ssh -p 9999 frappe@frappe.io "cd /home/frappe/frappe-bench/apps/frappe && git diff" | patch -p1
	for lang in get_all_languages():
		if lang!="en":
			print("exporting " + lang)
			edited = dict(frappe.db.sql("""select source, translated
				from `tabTranslated Message` where language=%s""", lang))
			for app in frappe.get_all_apps(True):
				path = os.path.join(frappe.get_app_path(app, "translations", lang + ".csv"))
				if os.path.exists(path):
					# only update existing strings
					current = dict(read_csv_file(path))

					for key in current:
						current[key] = edited.get(key) or current[key]

					write_translations_file(app, lang, current, sorted(list(current)))

def import_translations_from_file(lang, fname, editor):
	from frappe.translate import read_csv_file

	frappe.local.session.user = editor

	for m in read_csv_file(fname):
		src = frappe.db.get_value("Translated Message", {"language": lang, "source": m[0]}, ["name", "source", "translated"])
		if src and src[2] != m[1]:
			message = frappe.get_doc("Translated Message", src[0])
			message.translated = m[1]
			try:
				message.save()
				frappe.db.commit()
				print(src[1] + " updated")
			except frappe.ValidationError:
				print(src[1] + " ignored")
		else:
			message = frappe.new_doc("Translated Message")
			message.source = m[0]
			message.translated = m[1]
			message.language = lang
			print("saving", m[0])
			message.save()

def import_source_messages():
	"""Import messagse from apps listed in **Translator App** as **Source Message**"""
	frappe.db.sql("update `tabSource Message` set disabled=1")
	for app in frappe.db.sql_list("select name from `tabTranslator App`"):
		app_version = frappe.get_hooks(app_name='frappe')['app_version'][0]
		messages = get_messages_for_app(app)
		for message in messages:
			source_message = frappe.db.get_value("Source Message", {"message": message[1]}, ["name", "message", "position", "app_version"], as_dict=True)
			if source_message:
				d = frappe.get_doc("Source Message", source_message['name'])
				if source_message["position"] != message[0] or source_message["app_version"] != app_version:
					d.app_version = app_version
					d.position = message[0]
					d.app = app
				d.disabled = 0
			else:
				d = frappe.new_doc("Source Message")
				d.position = message[0]
				d.message = message[1]
				d.app = app
				d.app_version = app_version
			d.save()

def import_translated_from_text_files(untranslated_dir, translated_dir):
	def read_file(path):
		with open(path) as f:
			lines = [x.decode('utf-8-SIG').rstrip('\r\n') for x in f.readlines()]
			lines = [x for x in lines if x]
			return lines

	def restore_newlines(s):
		return (s.replace("||||||", "\n\n")
				.replace("| | | | | |", "\n\n")
				.replace("|||||", "\\\n")
				.replace("| | | | |", "\\\n")
				.replace("||||", "\\n")
				.replace("| | | |", "\\n")
				.replace("|||", "\n")
				.replace("| | |", "\n"))

	for lang in frappe.db.sql_list("select name from tabLanguage"):
		if lang == 'en':
			continue

		scache ={}
		for s, t in zip(read_file(os.path.join(untranslated_dir, lang+'.txt')), read_file(os.path.join(translated_dir, lang+'.txt'))):
			if scache.get(s):
				source = scache[s]
			else:
				source = frappe.db.get_value("Source Message", {"message": restore_newlines(s)})
				scache[s] = source
			dest = frappe.db.get_value("Translated Message", {"source": source, "language": lang})
			if not source:
				print('Cannot find source message for', s)
				continue

			if not get_placeholders_count(s) == get_placeholders_count(t):
				continue

			if dest:
				frappe.db.set_value("Translated Message", dest, "translated", restore_newlines(t))
			else:
				d = frappe.new_doc("Translated Message")
				d.language = lang
				d.translated = restore_newlines(t)
				d.source = source
				d.save()
		print('done for', lang)

def write_untranslated_csvs(path):
	for lang in frappe.db.sql_list("select name from tabLanguage"):
		write_untranslated_file(lang, os.path.join(path, lang+'.txt'))


def write_untranslated_file(lang, path):
	def escape_newlines(s):
		return (s.replace("\\\n", "|||||")
				.replace("\\n", "||||")
				.replace("\n", "|||"))

	with open(path, "w") as f:
		for m in get_untranslated(lang):
			# replace \n with ||| so that internal linebreaks don't get split
			f.write((escape_newlines(m) + os.linesep).encode("utf-8"))

def get_untranslated(lang):
	return frappe.db.sql("""select source.name, source.message from `tabSource Message` source
	left join `tabTranslated Message` translated on (source.name=translated.source and translated.language = %s)
	where translated.name is null and source.disabled != 1""", (lang, ))

def write_csv_for_all_languages():
	langs = frappe.db.sql_list("select name from tabLanguage")
	apps = frappe.db.sql_list("select name from `tabTranslator App`")
	for lang in langs:
		for app in apps:
			print("Writing for {0}-{1}".format(app, lang))
			write_csv(app, lang, frappe.utils.get_files_path("{0}-{1}.csv".format(app, lang)))

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
				
				w.writerow([t[0] if t[0] else '', t[1], strip(t[2] or '')])
				# w.writerow([t[0].encode('utf-8') if t[0] else '', t[1].encode('utf-8'), strip(t[2] or '').encode('utf-8')])

def get_translations_for_export(app, lang):
	return frappe.db.sql("""select
		source.position, source.message, translated.translated
	from `tabSource Message` source
		left join `tabTranslated Message` translated
			on (source.name=translated.source and translated.language = %s)
	where
		translated.name is not null
		and source.disabled != 1 and source.app = %s""", (lang, app))

def export_untranslated_to_json(lang, path):
	ret = {}
	for name, message in get_untranslated(lang):
		ret[name] = {
			"message": message.replace('$', '$$')
		}
	with open(path, 'wb') as f:
		json.dump(ret, f, indent=1)


def import_json(lang, path):
	"Imports translations from JSON. Only the new ones!"
	count = 0
	with open(path, 'rb') as f:
		messages = json.load(f)
	for source, message in iteritems(messages):
		if not frappe.db.get_value('Translated Message', {"source": source, "language": lang}):
			t = frappe.new_doc('Translated Message')
			t.language = lang
			t.source = source
			t.translated = message['message']
			t.save()
			count += 1
	print(count, 'imported')


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
	with open(path, 'rb') as f:
		reader = unicode_csv_reader(f)
		return list(reader)

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
	for row in csv_reader:
		yield [unicode(cell, 'utf-8') for cell in row]


def import_translations_from_csv(lang, path, modified_by='Administrator', if_older_than=None):
	content = read_translation_csv_file(path)
	if len(content[0]) == 2:
		content = [c for c in content if len(c) == 2]
		content = [('', c[0], c[1]) for c in content]
	count = 0
	print('importing', len(content), 'translations')
	for pos, source_message, translated in content:
		# print source_message.encode('utf-8'), translated.encode('utf-8')
		# try:
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

def get_languages_txt():
	return '\n'.join([
		'\t'.join([lang, name]) for lang, name in
		frappe.db.sql("select name, language_name from tabLanguage where name != 'en'")])
