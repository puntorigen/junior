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
        """Format the translated string with dynamic parameters, keeping placeholders intact."""
        # Temporarily replace placeholders with unique identifiers
        temp_text, unique_to_placeholder = self._replace_placeholders_with_unique(text, **kwargs)

        # Translate the modified text
        translated_temp_text = self.translate(temp_text)

        # Restore original placeholders in the final translation
        translated_text = self._restore_placeholders(translated_temp_text, unique_to_placeholder)

        # Update .po file using the original text (with actual placeholders)
        self.update_po_file(text, translated_text, self.target_lang, "Online" if self.online else "Offline")

        return translated_text.format(*args, **kwargs)

    def _replace_placeholders_with_unique(self, text, **kwargs):
        """Replace placeholders with unique identifiers."""
        unique_to_placeholder = {}
        for i, placeholder in enumerate(kwargs.keys()):
            unique_key = f'_PLACEHOLDER_{i}_'
            original_placeholder = f'{{{placeholder}}}'
            text = text.replace(original_placeholder, unique_key)
            unique_to_placeholder[unique_key] = original_placeholder
        return text, unique_to_placeholder

    def _restore_placeholders(self, text, unique_to_placeholder):
        """Restore unique identifiers back to original placeholders."""
        for unique_key, placeholder in unique_to_placeholder.items():
            text = text.replace(unique_key, placeholder)
        return text

    def update_po_file(self, original_text, translated_text, target_lang, method):
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
        entry = po.find(original_text)
        if entry is None:
            entry = polib.POEntry(msgid=original_text, msgstr=translated_text)
            po.append(entry)
        else:
            entry.msgstr = translated_text

        # Add translation method as a comment
        entry.comment = f'Translated using {method} translation.'

        # Remove entries with placeholders
        po = self._remove_placeholder_entries(po)

        # Save the updated .po file
        po.save(po_file_path)

        # Compile to .mo file
        po.save_as_mofile(mo_file_path)

    def _remove_placeholder_entries(self, po):
        """Remove entries with _PLACEHOLDER_ strings."""
        to_remove = [entry for entry in po if "_PLACEHOLDER_" in entry.msgid or "_PLACEHOLDER_" in entry.msgstr]
        for entry in to_remove:
            po.remove(entry)
        return po
