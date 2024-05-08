#import click
import sys, signal, os, time
#import gettext
#from .utils.brain import Brain
from .utils.localizer import Localizer
#from gettext import gettext as _
import rich_click as click
from rich import print
from yaspin import yaspin, Spinner
from yaspin.spinners import Spinners
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

# Localization setup (assuming locales are present)
locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
# Initialize Localizer
print("locales_dir:", locales_dir)
localizer = Localizer(locale_path=locales_dir, domain="messages")
_ = localizer.translate
test = _(f"Testing translation", target_lang="es")
print("test:", test)
#print("init translation service")
#trans = TranslationService(cache_dir=None)
#print("running translate offline")
#test = trans.translate_offline("Testing translation", target_lang="es")
#test = _(f"Testing translation", target_lang="es")
#target_lang = "en"   # Default language

# Determine if the output is being redirected (instead of terminal)
is_output_redirected = not sys.stdout.isatty()

# Determine which alias (bin/executable) was used
alias_used = os.path.basename(sys.argv[0])

def cleanup():
    # Perform cleanup here, such as removing temporary files
    pass

def signal_handler(sig, frame):
    click.echo(_('CTRL-C detected. Exiting gracefully.',target_lang=target_lang))
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

astral = Spinner(["⭐", "✨", "🌟", "🚀"], 200)

def process(text="Processing"):
    with yaspin(astral, text=f"[{alias_used}] {text}") as spinner:
        time.sleep(5)  # Simulate work
        spinner.text = f"[{alias_used}] {text}... done!"
        spinner.ok("✔")

@click.command()
@click.argument('input', type=str)
@click.option('--debug', '-d', is_flag=True, default=False, help="Run with :point_right: debug output")
@click.option('--language', '-l', type=str, default=None, help="Language for the output")
@click.option('--output-dir', '-o', type=str, default="", help="Directory to save output")
def cli(input, debug, language, output_dir):
    """Process the input"""
    global target_lang
    target_lang = "en"
    if language:
        target_lang = language
    else:
        from .utils.translator import TranslationService
        detect = TranslationService().detect_language
        input_text = " ".join(sys.argv[1:])
        try:
            target_lang = detect(input_text).lower()
            click.echo(f"Output language set to: {target_lang}")
        except Exception:
            target_lang = "en"
    click.echo(_(f"Target language set to: {target_lang}", target_lang=target_lang, online=False))

    # Your processing logic
    click.secho(f"Processing input: {input}", fg="green")
    process(f"Processing '{input}'")
    if debug:
        click.echo("Debug mode is on")
    if language:
        click.echo(f"Language: {language}")
    if output_dir:
        click.echo(f"Output directory: {output_dir}")

if __name__ == '__main__':
    cli()
