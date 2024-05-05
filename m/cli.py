import click
import sys, signal, os
import gettext
from gettext import gettext as _
from yaspin import yaspin, Spinner
from yaspin.spinners import Spinners
import time

is_output_redirected = not sys.stdout.isatty()

def cleanup():
    # Perform cleanup here, such as removing temporary files
    pass

def signal_handler(sig, frame):
    click.echo('CTRL-C detected. Exiting gracefully.')
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

astral = Spinner(["⭐", "✨", "🌟", "🚀"], 200)

def process(text="Processing"):
    with yaspin(astral, text=text) as spinner:
        time.sleep(5)  # Simulate work
        spinner.text = f"{text}... done!"
        spinner.ok("✔")

@click.command()
@click.argument('input', type=str)
@click.option('--debug', '-d', is_flag=True, default=False, help=_("Run with debug output"))
@click.option('--language', '-l', type=str, default="English", help=_("Language for the output"))
@click.option('--output-dir', '-o', type=str, default="", help=_("Directory to save output"))
def cli(input, debug, language, output_dir):
    """Process the input"""
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
