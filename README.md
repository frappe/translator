# Translator

Translation Portal for Frappe Apps

### To add a new language

1. Add a new **Language** via desk
2. `bench use translate.erpnext.com`
3. `bench translator translate-untranslated [language_code]`

### Update latest translations from apps

    bench translator import-source-messages

### Update missing translations

    bench translator translate-unstranslated-all

### Copy translations from one language to another

    bench translator copy-language [from] [to]

### Export

**On Remote:**

    bench --site translate.erpnext.com execute "translator.data.write_csv_for_all_languages"

**On local bench:**

    bench download-translations

