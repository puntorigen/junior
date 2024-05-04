generate-docs:
	pdoc --html m --output-dir docs

serve-docs:
	pdoc --http localhost:8080 m