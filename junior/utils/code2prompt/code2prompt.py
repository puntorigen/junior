# methods for traversing a given directory, its subdirectories and files, while ignoring those specified on .gitignore if available, or an array of glob files
# also to transform any binary file into a text file
# also to generate context variables as strings for LLMs such as source_tree, source_code, etc.
# also to generate a suitable prompt from a given code snippet (e.g. determine the language)
# also to provide methods for templates such as summarization, filefiltering, etc.

from datetime import datetime
from pathlib import Path
from fnmatch import fnmatch
from importlib import import_module

from junior.utils.code2prompt.comment_stripper import strip_comments
from junior.utils.code2prompt.language_inference import infer_language

class Code2Prompt:
    def __init__(self, path, gitignore=None, file_filter=None, suppress_comments=False):
        self.path = Path(path)
        self.gitignore_path = Path(gitignore) if gitignore else self.path / ".gitignore"
        self.gitignore_patterns = self.parse_gitignore(self.gitignore_path)
        self.gitignore_patterns.add(".git")
        self.file_filter = file_filter
        self.suppress_comments = suppress_comments
        self.parsers_dir = Path(__file__).parent / "parsers"

    @staticmethod
    def parse_gitignore(gitignore_path):
        """Parse the .gitignore file and return a set of patterns."""
        if not gitignore_path.exists():
            return set()

        with gitignore_path.open("r", encoding="utf-8") as file:
            patterns = set(
                line.strip() for line in file if line.strip() and not line.startswith("#")
            )
        return patterns

    @staticmethod
    def is_ignored(file_path: Path, gitignore_patterns: list, base_path: Path) -> bool:
        """Check if a file path matches any pattern in the .gitignore file."""
        relative_path = file_path.relative_to(base_path)

        for pattern in gitignore_patterns:
            pattern = pattern.rstrip("/")  # Remove trailing slash from the pattern

            if pattern.startswith("/"):
                if fnmatch(str(relative_path), pattern[1:]):
                    return True
                if fnmatch(str(relative_path.parent), pattern[1:]):
                    return True
            else:
                for path in relative_path.parents:
                    if fnmatch(str(path / relative_path.name), pattern):
                        return True
                    if fnmatch(str(path), pattern):
                        return True
                if fnmatch(str(relative_path), pattern):
                    return True

        return False

    @staticmethod
    def is_filtered(file_path, filter_pattern):
        """Check if a file path matches the filter pattern."""
        return fnmatch(file_path.name, filter_pattern)

    @staticmethod
    def is_binary(file_path):
        """Determines if the specified file is a binary file."""
        try:
            with open(file_path, "rb") as file:
                chunk = file.read(1024)
                return b"\x00" in chunk  # A file is considered binary if it contains a null byte
        except IOError:
            print(f"Error: The file at {file_path} could not be opened.")
            return False

    def find_parser(self, extension):
        """Dynamically find the parser module for a given file extension."""
        parser_module_name = f"{extension[1:]}_parser"
        try:
            parser_module = import_module(f".parsers.{parser_module_name}", package="m.utils.code2prompt")
            return getattr(parser_module, "parse_to_markdown")
        except (ImportError, AttributeError):
            return None

    def create_markdown_context(self):
        """Create a context object with content of files in a directory."""
        content = []
        table_of_contents = []

        for file_path in self.path.rglob("*"):
            if (
                file_path.is_file()
                and not self.is_ignored(file_path, self.gitignore_patterns, self.path)
                and (not self.file_filter or self.is_filtered(file_path, self.file_filter))
            ):
                file_extension = file_path.suffix
                file_size = file_path.stat().st_size
                file_creation_time = datetime.fromtimestamp(
                    file_path.stat().st_ctime
                ).strftime("%Y-%m-%d %H:%M:%S")
                file_modification_time = datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")

                try:
                    if self.is_binary(file_path):
                        parser = self.find_parser(file_extension)
                        if parser:
                            file_content = parser(file_path)
                        else:
                            file_content = "This binary file could not be parsed to text."
                    else:
                        with file_path.open("r", encoding="utf-8") as f:
                            file_content = f.read()
                            if self.suppress_comments:
                                language = infer_language(file_path.name)
                                if language != "unknown":
                                    file_content = strip_comments(file_content, language)
                except UnicodeDecodeError:
                    continue  # Ignore files that cannot be decoded

                file_info = {
                    "path": str(file_path),
                    "extension": file_extension,
                    "size": file_size,
                    "created": file_creation_time,
                    "modified": file_modification_time,
                }

                language = infer_language(file_path.name)
                if language == "unknown":
                    language = file_extension[1:]

                file_code = {
                    "language": language,
                    "content": file_content
                }

                content.append({
                    "info": file_info,
                    "code": file_code
                })

                table_of_contents.append(f"- [{file_path}](#{file_path.as_posix().replace('/', '')})\n")

        context = {
            "table_of_contents": "".join(table_of_contents),
            "files": content
        }

        return context

    def create_markdown_file(self, output=None):
        """Create a Markdown file with the content of files in a directory."""
        context = self.create_markdown_context()
        markdown_content = "# Table of Contents\n" + context["table_of_contents"] + "\n"

        for file_entry in context["files"]:
            file_info = file_entry["info"]
            file_code = file_entry["code"]

            markdown_content += f"## File: {file_info['path']}\n\n"
            markdown_content += f"- Extension: {file_info['extension']}\n"
            markdown_content += f"- Size: {file_info['size']} bytes\n"
            markdown_content += f"- Created: {file_info['created']}\n"
            markdown_content += f"- Modified: {file_info['modified']}\n\n"
            markdown_content += f"### Code\n```{file_code['language']}\n{file_code['content']}\n```\n\n"

        if output:
            output_path = Path(output)
            with output_path.open("w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)
            print(f"Markdown file '{output_path}' created successfully.")
        else:
            print(markdown_content)
