from junior.cli_manager import CLIManager
from junior.utils.setup import Setup
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
    setup = Setup(language=click.target_lang)
    setup.run_initial_setup()
    click.log("loaded settings: ",setup.settings)
    #click.echo("[yellow]Processing input:[/yellow] {input}", input=input)
    click.echo("*Processing input:* {input}", input=input)
    def task_test():
        total_steps = 10
        for i in range(total_steps):
            yield ("_Processing_ *step* {from}/{total}", { "from":i+1, "total": total_steps })
            time.sleep(0.5)

    click.log("Starting *process*... :smiley:", { "name":"Pablo" })
    click.process(task_test, "Working on '{input}'", input=input)

    if debug:
        click.echo("Debug mode is on")
    if output_dir:
        click.echo("Output directory: {output_dir}", output_dir=output_dir)

if __name__ == '__main__':
    cli()
