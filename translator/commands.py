# Copyright (c) 2015, Web Notes Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, absolute_import
from frappe.commands import pass_context
from translator.data import (import_source_messages, export_untranslated_to_json,
	import_translations_from_csv, translate_untranslated_from_google, copy_translations)
from frappe.translate import get_bench_dir
import frappe.utils.data
import requests.exceptions
import click
import os


@click.command('import-source-messages')
@pass_context
def _import_source_messages(context):
	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			import_source_messages()
			frappe.db.commit()
		finally:
			frappe.destroy()


@click.command('export-untranslated')
@pass_context
def _export_untranslated_to_json(context):
	untranslated_dir = os.path.abspath(os.path.join(get_bench_dir(), 'untranslated'))
	if not os.path.exists(untranslated_dir):
		os.mkdir(untranslated_dir)

	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			for lang in frappe.db.sql_list("select name from `tabLanguage`"):
				export_untranslated_to_json(lang, os.path.join(untranslated_dir, lang + '.json'))
		finally:
			frappe.destroy()


@click.command('import-from-csv')
@click.argument('lang')
@click.argument('csv-file')
@click.option('--if-older-than')
@pass_context
def _import_translations_from_csv(context, lang, csv_file, if_older_than=None):
	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			if if_older_than:
				if_older_than = frappe.utils.data.get_datetime(if_older_than)
			import_translations_from_csv(lang, csv_file, if_older_than=if_older_than)
			frappe.db.commit()
		finally:
			frappe.destroy()


@click.command('translate-untranslated')
@click.argument('lang')
@pass_context
def _translate_untranslated(context, lang):
	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			translate_untranslated_from_google(lang)
			frappe.db.commit()
		finally:
			frappe.destroy()

@click.command('copy-translations')
@click.argument('from_lang')
@click.argument('to_lang')
@pass_context
def _copy_translations(context, from_lang, to_lang):
	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			copy_translations(from_lang, to_lang)
			frappe.db.commit()
		finally:
			frappe.destroy()


@click.command('translate-untranslated-all')
@pass_context
def _translate_untranslated_all(context):
	for site in context.sites:
		try:
			frappe.init(site=site)
			frappe.connect()
			for lang in frappe.db.sql_list("select name from tabLanguage"):
				try:
					translate_untranslated_from_google(lang)
				except requests.exceptions.HTTPError:
					print "skipping {0}".format(lang)
					continue
				finally:
					frappe.db.commit()
		finally:
			frappe.destroy()

commands = [
	_import_source_messages,
	_export_untranslated_to_json,
	_import_translations_from_csv,
	_translate_untranslated,
	_translate_untranslated_all,
]
