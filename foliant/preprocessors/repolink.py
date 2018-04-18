'''
Preprocessor for Foliant documentation authoring tool.

Allows to add a hyperlink to related file in Git repository
into Markdown source.

Provides ``repo_url`` and ``edit_uri`` options, same as MkDocs.
Applies the styling like used in Material MkDocs theme
to generated hyperlink.

Useful for projects generated from multiple sources.
'''

import re
from pathlib import Path

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'repo_url': '',
        'edit_uri': '/blob/master/src/',
        'link_text': 'Edit this page',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _add_repo_link(self, markdown_file_relative_path: str, content: str) -> str:
        if self.options['repo_url']:
            repo_url = self.options['repo_url'].rstrip('/')
            edit_uri = self.options['edit_uri'].strip('/')
            repo_url_with_edit_uri = f'{repo_url}/{edit_uri}'.rstrip('/')

            first_heading_pattern = re.compile(
                "^(?P<first_heading>\s*#{1,6}[ \t]+([^\r\n]+?)(?:[ \t]+\{#\S+\})?\s*[\r\n]+)"
            )

            content = re.sub(
                first_heading_pattern,
                f'\g<first_heading>\n\n<a href="{repo_url_with_edit_uri}/{markdown_file_relative_path}" ' \
                f'title="{self.options["link_text"]}" class="md-icon md-content__icon" ' \
                f'style="margin: -7.5rem 0">&#xE3C9;</a>\n\n',
                content
            )

        return content

    def apply(self):
        if self.context['backend'] != 'pandoc':
            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    content = markdown_file.read()

                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(self._add_repo_link(f'{markdown_file_path.relative_to(self.working_dir)}', content))
