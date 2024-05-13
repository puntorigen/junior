import os, sys, time, re
import rich_click as click
from rich import print
from yaspin import yaspin, Spinner
from .utils.localizer import Localizer
from .utils.translator import TranslationService

class CLIManager:
    def __init__(self, debug=True, debug_prefix="DEBUG"):
        self.configure_rich_click()
        self.debug = debug
        self.debug_prefix = debug_prefix
        self.target_lang = "en"
        locales_dir = os.path.join(os.path.dirname(__file__), "locales")
        self.localizer = Localizer(locale_path=locales_dir, domain="cli", target_lang=self.target_lang, online=True)
        self.translator = TranslationService()
        self.input_text_english = ""
        self.color_mapping = {
            "*": "yellow",
            "_": "i"
        }
        self._ = self.localizer._
        self.spinner = Spinner(["⭐", "✨", "🌟", "🚀"], 200)

    def configure_rich_click(self):
        """Configure rich_click with all necessary styles and settings."""
        click.rich_click.USE_RICH_MARKUP = True
        click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
        click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
        #click.rich_click.ERRORS_EPILOGUE = "To find out more, visit [link=https://www.puntorigen.com/m]https://www.puntorigen.com/m[/link]"
        #click.rich_click.SHOW_ARGUMENTS = True
        #click.rich_click.STYLE_OPTIONS_TABLE_LEADING = 1
        #click.rich_click.STYLE_OPTIONS_TABLE_BOX = "SIMPLE"
        click.rich_click.STYLE_OPTIONS_TABLE_ROW_STYLES = ["bold", ""]
        click.rich_click.STYLE_COMMANDS_TABLE_SHOW_LINES = True
        click.rich_click.STYLE_COMMANDS_TABLE_PAD_EDGE = True
        click.rich_click.STYLE_COMMANDS_TABLE_BOX = "DOUBLE"
        click.rich_click.STYLE_COMMANDS_TABLE_BORDER_STYLE = "red"
        click.rich_click.STYLE_COMMANDS_TABLE_ROW_STYLES = ["magenta", "yellow", "cyan", "green"]

    def setColorTokens(self, token_colors):
        """Set the token to color mappings."""
        self.color_mapping = token_colors

    def apply_color(self, text):
        """Wrap tokens with rich color tags based on the mappings."""
        for token, color in self.color_mapping.items():
            # Create a regex pattern that matches pairs of the token with at least one non-token character between them
            pattern = re.compile(f'\\{token}([^\\{token}]+)\\{token}')
            # Replace each found pair with Rich formatted color tags
            text = pattern.sub(f'[{color}]\\1[/]', text)
        return text 

    def echo(self, text, *args, **kwargs):
        """Echo messages with translation and formatting."""
        # Translates the text and uses args and kwargs for formatting
        translated_text = self._(text, *args, **kwargs)
        # Apply color formatting
        formatted_text = self.apply_color(translated_text)
        # Print the formatted text with 'Rich' support
        print(formatted_text)
    
    def debug_(self, text, *args, **kwargs):
        """Echo debug messages with formatting."""
        # Apply color formatting
        formatted_text = self.apply_color(text)
        if not self.debug:
            return
        formatted_text = f"[green]{self.debug_prefix}:[/] [dim]{formatted_text.format(*args, **kwargs)}[/]"
        # Print the formatted text with 'Rich' support
        print(formatted_text)

    def translate(self, text, target_lang="en", online=True):
        """Translate text (to english) using the shared TranslationService."""
        target_lang = target_lang if target_lang else self.target_lang
        detected_lang = self.translator.detect_language(text)
        if target_lang != detected_lang:
            return self.translator.translate(text, target_lang=target_lang, online=online)
        return text

    def process(self, text):
        """Process function with spinner."""
        with yaspin(self.spinner, text=text) as spinner:
            # Simulated work
            spinner.text = text + "... done!"
            spinner.ok("✔")

    def setup_language(self, input_text, language=None):
        """Detect and set language for output based on input or specified language."""
        if language:
            self.target_lang = language
        else:
            detected_lang = self.translator.detect_language(input_text).lower()
            self.target_lang = detected_lang
            self.input_text_english = input_text
            if detected_lang != "en":
                self.input_text_english = self.translate(input_text)
                self.debug_(f"Input text in _English_: {self.input_text_english}")
        self.localizer.target_lang = self.target_lang
        self.debug_(f"Output language set to: _{self.target_lang}_")

    def command(self, *args, **kwargs):
        """Decorator to wrap rich_click command."""
        return click.command(*args, **kwargs)

    def option(self, *args, **kwargs):
        """Decorator to wrap rich_click option."""
        return click.option(*args, **kwargs)

    def argument(self, *args, **kwargs):
        """Decorator to wrap rich_click argument."""
        return click.argument(*args, **kwargs)
