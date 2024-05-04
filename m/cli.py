import click
import sys, signal, os
import gettext
from gettext import gettext as _

is_output_redirected = not sys.stdout.isatty()

def cleanup():
    # Perform cleanup here, such as removing temporary files
    pass

def signal_handler(sig, frame):
    click.echo('CTRL-C detected. Exiting gracefully.')
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

@click.command()
@click.argument('input', type=str)
@click.option('--debug', '-d', is_flag=True, default=False, help=_("Run with debug output"))
@click.option('--language', '-l', type=str, default="English", help=_("Language for the output"))
@click.option('--output-dir', '-o', type=str, default="", help=_("Directory to save output"))
def cli(input, debug, language, output_dir):
    """Process the input"""
    # Your processing logic
    click.echo(f"Processing input: {input}")
    if debug:
        click.echo("Debug mode is on")
    if language:
        click.echo(f"Language: {language}")
    if output_dir:
        click.echo(f"Output directory: {output_dir}")

if __name__ == '__main__':
    cli()
