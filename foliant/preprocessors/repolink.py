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
        'link_type': 'html',
        'link_location': 'after_first_heading',
        'link_text': 'Edit this page',
        'link_title': 'Edit this page',
        'link_html_attributes': '',
        'targets': [],
    }

    tags = 'repo_link',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('repolink')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def add_repo_link(self, markdown_file_relative_path: Path, content: str) -> str:
        if self.options['repo_url']:
            repo_url = self.options['repo_url'].rstrip('/')
            edit_uri = getenv('FOLIANT_REPOLINK_EDIT_URI', self.options['edit_uri']).strip('/')

            link_href = (
                (
                    self.options['repo_url'].rstrip('/') +
                    '/' +
                    getenv('FOLIANT_REPOLINK_EDIT_URI', self.options['edit_uri']).strip('/')
                ).rstrip('/') +
                '/' +
                markdown_file_relative_path
            )

            self.logger.debug(
                f'Link href: {link_href}'
            )

            if self.options['link_type'] == 'html':
                link_html_attributes = self.options['link_html_attributes']

                if link_html_attributes:
                    link_html_attributes = ' ' + link_html_attributes

                self.logger.debug(
                    'Generating HTML link, ' +
                    f'text: {self.options["link_text"]}, ' +
                    f'title: {self.options["link_title"]}, ' +
                    f'attributes: {link_html_attributes}'
                )

                link = (
                    f'<a href="{link_href}" ' +
                    f'title="{self.options["link_title"]}"{link_html_attributes}>{self.options["link_text"]}</a>'
                )

            elif self.options['link_type'] == 'markdown':
                self.logger.debug(f'Generating Markdown link, text: {self.options["link_text"]}')

                link = f'[{self.options["link_text"]}]({link_href})'

            else:
                self.logger.debug('Unrecognized link type specified, skipping')

                return content

            if self.options['link_location'] == 'after_first_heading':
                self.logger.debug('Locating the link after the first heading')

                heading_pattern = re.compile(
                    r'^(?P<heading>\#{1,6}\s+.*\S+\s*)$',
                    flags=re.MULTILINE
                )

                content = re.sub(
                    heading_pattern,
                    f'\g<heading>\n\n{link}\n\n',
                    content,
                    count=1
                )

            elif self.options['link_location'] == 'before_content':
                self.logger.debug('Placing the link before the content')

                content = f'{link}\n\n{content}'

            elif self.options['link_location'] == 'after_content':
                self.logger.debug('Placing the link after the content')

                content = f'{content}\n\n{link}\n'

            elif self.options['link_location'] == 'defined_by_tag':
                self.logger.debug('Link locations are defined by tags')

                content = self.pattern.sub(link, content)

            else:
                self.logger.debug('Unrecognized link location, skipping')

        else:
            self.logger.debug('Repo URL is not specified, skipping')

        return content

    def apply(self):
        self.logger.info('Applying preprocessor')

        self.logger.debug(f'Allowed targets: {self.options["targets"]}')
        self.logger.debug(f'Current target: {self.context["target"]}')

        if not self.options['targets'] or self.context['target'] in self.options['targets']:
            for markdown_file_path in self.working_dir.rglob('*.md'):
                self.logger.debug(f'Processing the file: {markdown_file_path}')

                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    content = markdown_file.read()

                processed_content = self.add_repo_link(
                    f'{markdown_file_path.relative_to(self.working_dir)}', content
                )

                if processed_content:
                    with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                        markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied')
