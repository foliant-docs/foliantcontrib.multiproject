'''
Preprocessor for Foliant documentation authoring tool.

Allows to add a hyperlink to related file in Git repository
into Markdown source.

Provides ``repo_url`` and ``edit_uri`` options, same as MkDocs.
The ``edit_uri`` option may be overridden with the
``FOLIANT_REPOLINK_EDIT_URI`` system environment variable.

Useful for projects generated from multiple sources.
'''

import re
from os import getenv
from pathlib import Path

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'repo_url': '',
        'edit_uri': '/blob/master/src/',
        'link_text': 'Edit this page',
        'link_title': 'Edit this page',
        'link_html_attributes': '',
        'targets': [],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('repolink')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def add_repo_link(self, markdown_file_relative_path: str, content: str) -> str:
        if self.options['repo_url']:
            repo_url = self.options['repo_url'].rstrip('/')
            edit_uri = getenv('FOLIANT_REPOLINK_EDIT_URI', self.options['edit_uri']).strip('/')
            repo_url_with_edit_uri = f'{repo_url}/{edit_uri}'.rstrip('/')

            link_html_attributes = self.options['link_html_attributes']

            self.logger.debug(f'Link href: {repo_url_with_edit_uri}/{markdown_file_relative_path}')
            self.logger.debug(f'Link attributes: {link_html_attributes}')
            self.logger.debug(f'Link text: {self.options["link_text"]}')
            self.logger.debug(f'Link title: {self.options["link_title"]}')

            if link_html_attributes:
                link_html_attributes = ' ' + link_html_attributes

            first_heading_pattern = re.compile(
                "^(?P<first_heading>\s*#{1,6}[ \t]+([^\r\n]+?)(?:[ \t]+\{#\S+\})?\s*[\r\n]+)"
            )

            content = re.sub(
                first_heading_pattern,
                f'\g<first_heading>\n\n<a href="{repo_url_with_edit_uri}/{markdown_file_relative_path}" ' \
                f'title="{self.options["link_title"]}"{link_html_attributes}>{self.options["link_text"]}</a>\n\n',
                content
            )

        return content

    def apply(self):
        self.logger.info('Applying preprocessor')

        self.logger.debug(f'Allowed targets: {self.options["targets"]}')
        self.logger.debug(f'Current target: {self.context["target"]}')

        if not self.options['targets'] or self.context['target'] in self.options['targets']:
            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    content = markdown_file.read()

                processed_content = self.add_repo_link(
                    f'{markdown_file_path.relative_to(self.working_dir)}', content
                )

                if processed_content:
                    with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                        markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied')
