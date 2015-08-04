# Translator

Translation Portal for Frappe Apps

### To add a new language

1. Add a new **Language** via desk
2. `bench use translate.erpnext.com`
3. `bench translate get-untranslated [language_code]`
4. Update missing translations (new messages) `bench translator translate-untranslated-all`

### Export

**On Remote:**

    bench --site translate.erpnext.com execute "translator.data.write_csv_for_all_languages"

**On local bench:**

    bench download-translations`

