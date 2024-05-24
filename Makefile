dev:
	pip install wheel setuptools pip --upgrade
	pip install -r requirements.txt
	pip install -e .

generate-docs:
	pdoc --html junior --output-dir docs

serve-docs:
	pdoc --http localhost:8080 junior