'''
Preprocessor for Foliant documentation authoring tool.

Allows to add a hyperlink to related file in Git repository
into Markdown source.

Provides ``repo_url`` and ``edit_uri`` options, same as MkDocs.
Useful for projects generated from multiple sources.
'''

from pathlib import Path

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'repo_url': '',
        'edit_uri': '/blob/master/src/',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_repo_link(self, markdown_file_name: str, content: str) -> str:
        if self.options['repo_url']:
            repo_url = self.options['repo_url'].rstrip('/')
            edit_uri = self.options['edit_uri'].strip('/')
            repo_url_with_edit_uri = f'{repo_url}/{edit_uri}'.rstrip('/')

            content += f'\n\n[Edit]({repo_url_with_edit_uri}/{markdown_file_name})'

        return content

    def apply(self):
        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(self.add_repo_link(markdown_file_path.name, content))
