import mistune
import junior.utils.code_executor

class MyRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        return {'type': 'block_code', 'text': code, 'language': info}

markdown = mistune.create_markdown(renderer=MyRenderer())

def process_file(filename):
    with open(filename, 'r') as file:
        parsed = markdown(file.read())

    for block in parsed:
        if block['type'] == 'block_code':
            result = code_executor.execute(block['text'], block['language'])
            print(result)
