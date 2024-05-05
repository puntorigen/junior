from setuptools import setup, find_packages

setup(
    name='m-ai-cli',
    version='0.1.0',
    description='An interactive AI based CLI for working with your local files and folders',
    author='Pablo Schaffner',
    author_email='pablo@puntorigen.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'm = m.cli:cli', #Main personality
            'p = m.cli:cli', #Pablo personality
            'q = m.cli:cli', #Q personality
        ],
    },
    install_requires=[
        'click',
        'mistune',
        'restrictedpython',
        'babel',
    ],
    python_requires='>=3.7, <4',
)
