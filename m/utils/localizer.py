# localizer.py
import os
import polib
import gettext
from .translator import TranslationService

class Localizer:
    def __init__(self, locale_path='locales', domain='messages', cache_dir=None, cache_ttl=3600, target_lang='en', online=True):
        self.locale_path = locale_path
        self.domain = domain
        self.translator = TranslationService(cache_dir=cache_dir, cache_ttl=cache_ttl)
        self.target_lang = target_lang
        self.online = online

        # Configure gettext
        gettext.bindtextdomain(domain, locale_path)
        gettext.textdomain(domain)

    def translate(self, text):
        """Translate the given text using gettext with fallback translation."""
        translated_text = gettext.gettext(text)

        if translated_text == text:  # No translation found in .mo files
            translated_text = self.translator.translate(text, target_lang=self.target_lang, online=self.online)
            translation_method = "Online" if self.online else "Offline"
            self.update_po_file(text, translated_text, self.target_lang, translation_method)

        return translated_text

    def _(self, text, *args, **kwargs):
        """Format the translated string with dynamic parameters, mimicking the gettext `_` function, keeping placeholders intact."""
        translated_text = self.translate(text)
        return translated_text.format(*args, **kwargs)

    def update_po_file(self, text, translation, target_lang, method):
        """Update the .po file with a new translation and recompile to .mo."""
        po_file_path = os.path.join(self.locale_path, target_lang, 'LC_MESSAGES', f'{self.domain}.po')
        mo_file_path = os.path.join(self.locale_path, target_lang, 'LC_MESSAGES', f'{self.domain}.mo')

        # Ensure the directory exists
        os.makedirs(os.path.dirname(po_file_path), exist_ok=True)

        # Load or create the .po file
        if os.path.exists(po_file_path):
            po = polib.pofile(po_file_path)
        else:
            po = polib.POFile()
            po.metadata = {
                'Project-Id-Version': '1.0',
                'Report-Msgid-Bugs-To': '',
                'POT-Creation-Date': '',
                'PO-Revision-Date': '',
                'Last-Translator': '',
                'Language-Team': '',
                'MIME-Version': '1.0',
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding': '8bit',
                'Language': target_lang,
            }

        # Find or create the entry
        entry = po.find(text)
        if entry is None:
            entry = polib.POEntry(msgid=text, msgstr=translation)
            po.append(entry)
        else:
            entry.msgstr = translation

        # Add translation method as a comment
        entry.comment = f'Translated using {method} translation.'

        # Save the updated .po file
        po.save(po_file_path)

        # Compile to .mo file
        po.save_as_mofile(mo_file_path)
