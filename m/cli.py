import click
from . import markdown_processor

@click.group()
def m():
    pass

@m.command()
@click.argument('filename')
def process_markdown(filename):
    markdown_processor.process_file(filename)

if __name__ == '__main__':
    m()
