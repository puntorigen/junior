import subprocess
from RestrictedPython import compile_restricted, safe_globals

def execute(code, language):
    if language == 'python':
        return execute_python(code)
    elif language == 'javascript':
        return execute_javascript(code)
    else:
        raise ValueError(f"Unsupported language: {language}")

def execute_python(code):
    byte_code = compile_restricted(code, '<inline>', 'exec')
    global_env = safe_globals
    local_env = {}
    exec(byte_code, global_env, local_env)
    return local_env

def execute_javascript(code):
    result = subprocess.run(['node', '-e', code], capture_output=True, text=True)
    return result.stdout
