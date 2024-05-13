from .cli_manager import CLIManager
import sys, signal, os, time
click = CLIManager()
#from .utils.brain import Brain
#from rich import print

# Determine if the output is being redirected (instead of terminal)
is_output_redirected = not sys.stdout.isatty()

# Determine which alias (bin/executable) was used
alias_used = os.path.basename(sys.argv[0])

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
@click.option('--debug', '-d', is_flag=True, default=False, help="Run with :point_right: debug output")
@click.option('--language', '-l', type=str, default=None, help="Language for the output")
@click.option('--output-dir', '-o', type=str, default="", help="Directory to save output")
def cli(input, debug, language, output_dir):
    """Process the input"""
    click.setup_language(input, language)
    #click.echo("[yellow]Processing input:[/yellow] {input}", input=input)
    click.echo("*Processing input:* {input}", input=input)
    click.process(f"Working on '{input}'")
    if debug:
        click.echo("Debug mode is on")
    if output_dir:
        click.echo("Output directory: {output_dir}", output_dir=output_dir)

if __name__ == '__main__':
    cli()
