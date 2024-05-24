import os, re
from typing import List, Dict, Optional, Tuple

class ProjectType:
    REACT = 'React.js Project'
    NEXT = 'Next.js Project'
    NUXT = 'Nuxt.js Project'
    VUE = 'Vue.js Project'
    PYTHON_CLI = 'Python CLI'
    PYTHON_PACKAGE = 'Python Package'
    DOCUMENTATION = 'Documentation'
    OTHER = 'Other'
    DESKTOP = 'User Desktop Folder'
    DOCUMENTS = 'User Documents Folder'
    MSFILES = 'Microsoft Office Files'
    UNKNOWN = 'Unknown'

# Mapping of folder types to identifying files
PROJECT_SIGNATURES: Dict[str, List[Tuple[str, Optional[re.Pattern]]]] = {
    ProjectType.REACT: [
        ('package.json', re.compile(r'"react"')),
    ],
    ProjectType.NEXT: [
        ('package.json', re.compile(r'"next"')),
    ],
    ProjectType.NUXT: [
        ('package.json', re.compile(r'"nuxt"')),
    ],
    ProjectType.VUE: [
        ('package.json', re.compile(r'"vue"')),
    ],
    ProjectType.PYTHON_CLI: [
        ('setup.py', None),
        ('pyproject.toml', None),
        ('main.py', None),
    ],
    ProjectType.PYTHON_PACKAGE: [
        ('setup.py', None),
        ('pyproject.toml', None),
        ('__init__.py', None),
    ],
    ProjectType.DOCUMENTATION: [
        ('README.md', None),
        ('docs', None),
    ],
    ProjectType.DESKTOP: [
        ('Desktop', None),
    ],
    ProjectType.DOCUMENTS: [
        ('Documents', None),
    ],
    ProjectType.MSFILES: [],
}

# Mapping of project types to relevant files for detailed analysis
PROJECT_FILES: Dict[str, List[str]] = {
    ProjectType.REACT: ['package.json', 'src/index.js', 'README.md'],
    ProjectType.NEXT: ['package.json', 'next.config.js', 'README.md'],
    ProjectType.NUXT: ['package.json', 'nuxt.config.js', 'README.md'],
    ProjectType.VUE: ['package.json', 'vue.config.js', 'README.md'],
    ProjectType.PYTHON_CLI: ['setup.py', 'main.py', 'README.md'],
    ProjectType.PYTHON_PACKAGE: ['setup.py', '__init__.py', 'README.md'],
    ProjectType.DOCUMENTATION: ['README.md', 'docs/index.md'],
    ProjectType.MSFILES: ['*.docx', '*.pptx', '*.xlsx', '*.pdf'],
}

# Microsoft Office-related file extensions
MSFILE_EXTENSIONS = {'.docx', '.pptx', '.xlsx', '.pdf'}

def identify_project_type(folder: str) -> str:
    # Check for project types based on signatures
    for project_type, signatures in PROJECT_SIGNATURES.items():
        for filename, pattern in signatures:
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                if pattern is None:
                    return project_type
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if pattern.search(content):
                    return project_type
            elif os.path.isdir(file_path) and pattern is None:
                return project_type

    # Check if the folder only contains MS files
    if contains_only_ms_files(folder):
        return ProjectType.MSFILES

    return ProjectType.UNKNOWN

def contains_only_ms_files(folder: str) -> bool:
    """
    Checks if the folder contains only Microsoft Office-related files.

    Args:
        folder (str): The folder path to check.

    Returns:
        bool: True if the folder only contains MS files, False otherwise.
    """
    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return False

    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() not in MSFILE_EXTENSIONS:
            return False
    return True

def get_relevant_files(folder: str) -> List[str]:
    project_type = identify_project_type(folder)
    relevant_files = PROJECT_FILES.get(project_type, [])
    # Handle wildcard patterns
    resolved_files = []
    for pattern in relevant_files:
        if '*' in pattern:
            resolved_files.extend(glob_files(folder, pattern))
        else:
            file_path = os.path.join(folder, pattern)
            if os.path.exists(file_path):
                resolved_files.append(file_path)
    return resolved_files

def glob_files(folder: str, pattern: str) -> List[str]:
    import glob
    return glob.glob(os.path.join(folder, pattern))

def analyze_folder(folder: str) -> None:
    project_type = identify_project_type(folder)
    relevant_files = get_relevant_files(folder)

    print(f'Folder: {folder}')
    print(f'Identified Project Type: {project_type}')
    print(f'Relevant Files: {relevant_files}')

# Example usage
if __name__ == '__main__':
    folder_path = '/path/to/folder'
    analyze_folder(folder_path)
