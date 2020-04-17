'''
Extension for Foliant to generate the documentation from multiple sources.

Resolves ``!from`` YAML tag in the project config.
Replaces the value of the tag with ``chaptres`` section
of related subproject. The subproject location may be
specified as a local path, or as a Git repository with
optional revision (branch name, commit hash or another
reference). Examples: ``local_path``,
``https://github.com/foliant-docs/docs.git``,
``https://github.com/foliant-docs/docs.git#master``.
'''

from yaml import add_constructor, load, Loader, BaseLoader
from shutil import copytree, move, rmtree
from os import chdir, getcwd
from pathlib import Path
from logging import DEBUG
from importlib import import_module
from subprocess import run, CalledProcessError, PIPE, STDOUT

from foliant.config.base import BaseParser


class Parser(BaseParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._src_dir_name = Path(self._get_multiproject_config()['src_dir']).name
        self._cache_dir_name = '.multiprojectcache'
        self._config_file_name = self.config_path.name

        add_constructor('!from', self._resolve_from_tag_to_build)

    def _get_multiproject_config(self) -> dict:
        self.logger.debug('Getting config of the multiproject')

        with open(self.config_path.resolve()) as multiproject_config_file:
            multiproject_config = {**self._defaults, **load(multiproject_config_file, Loader=BaseLoader)}

            self.logger.debug(f'Config of the multiproject: {multiproject_config}')

            return multiproject_config

    def _get_subproject_config(
            self,
            subproject_cached_dir_path: Path,
            previous_subproject_cached_dir_path: Path or None = None
        ) -> dict:
        self.logger.debug(
            f'Subprojects to get config, current: {subproject_cached_dir_path}, ' +
            f'previous: {previous_subproject_cached_dir_path}'
        )

        def _resolve_from_tag_to_get_chapters(loader, node):
            nested_subproject_pointer = node.value

            self.logger.debug(
                f'Nested subproject detected, pointer: {nested_subproject_pointer}, getting path'
            )

            nested_subproject_cached_dir_path = self._get_cached_subproject_dir_path(
                nested_subproject_pointer,
                subproject_cached_dir_path
            )

            self.logger.debug(f'Path of nested subproject to get config: {nested_subproject_cached_dir_path}')

            previous_subproject_cached_dir_path = subproject_cached_dir_path

            nested_subproject_config = self._get_subproject_config(
                nested_subproject_cached_dir_path,
                previous_subproject_cached_dir_path
            )

            self.logger.debug(f'Config of nested subproject: {nested_subproject_config}')

            nested_subproject_chapters = {
                nested_subproject_config.get('title', ''): self._get_chapters_with_overwritten_paths(
                    nested_subproject_config.get('chapters', []),
                    nested_subproject_cached_dir_path
                )
            }

            self.logger.debug(f'Chapters of nested subproject: {nested_subproject_chapters}')

            return nested_subproject_chapters

        add_constructor('!from', _resolve_from_tag_to_get_chapters)

        subproject_config_file_path = (
            subproject_cached_dir_path / self._config_file_name
        ).resolve()

        self.logger.debug(f'Reading subproject config file: {subproject_config_file_path}')

        with open(subproject_config_file_path) as subproject_config_file:
            subproject_config = load(subproject_config_file, Loader)

        self.logger.debug(f'Subproject config: {subproject_config}')

        subproject_cached_dir_path = previous_subproject_cached_dir_path

        return subproject_config

    def _resolve_from_tag_to_build(self, loader, node) -> dict:
        subproject_pointer = node.value

        self.logger.debug(f'Pointer of subproject to build: {subproject_pointer}, getting path')

        subproject_cached_dir_path = self._get_cached_subproject_dir_path(
            subproject_pointer,
            self.project_path.resolve()
        )

        self.logger.debug(f'Path of subproject to build: {subproject_cached_dir_path}, getting config')

        subproject_config = self._get_subproject_config(subproject_cached_dir_path)

        self.logger.debug(f'Config of subproject to build: {subproject_config}')

        subproject_chapters = {
            subproject_config.get('title', ''): self._get_chapters_with_overwritten_paths(
                subproject_config.get('chapters', []), subproject_cached_dir_path
            )
        }

        self.logger.debug(f'Chapters of subproject to build: {subproject_chapters}, building the subproject')

        subproject_built_dir_path = (
            subproject_cached_dir_path / self._build_subproject(subproject_cached_dir_path)
        ).resolve()

        self.__init__(
            project_path=self.project_path,
            config_file_name=self._config_file_name,
            logger=self.logger,
            quiet=self.quiet
        )

        subproject_target_dir_path = (
            self.project_path / self._src_dir_name / subproject_cached_dir_path.name
        ).resolve()

        self.logger.debug(
            f'Moving built subproject from {subproject_built_dir_path} to {subproject_target_dir_path}'
        )

        rmtree(subproject_target_dir_path, ignore_errors=True)
        move(subproject_built_dir_path, subproject_target_dir_path)

        return subproject_chapters

    def _build_subproject(self, subproject_cached_dir_path: Path) -> str:
        self.logger.debug(
            f'Calling Foliant to build the subproject that is located at: {subproject_cached_dir_path}'
        )

        source_cwd = getcwd()
        chdir(subproject_cached_dir_path)

        subproject_debug_mode = True if self.logger.getEffectiveLevel() == DEBUG else False

        foliant_cli_module = import_module('foliant.cli')

        subproject_built_dir_name = foliant_cli_module.Foliant().make(
            target='pre',
            project_path=subproject_cached_dir_path,
            quiet=self.quiet,
            keep_tmp=True,
            debug=subproject_debug_mode
        )

        chdir(source_cwd)

        return subproject_built_dir_name

    def _get_cached_subproject_dir_path(
        self,
        subproject_pointer: str,
        multiproject_dir_path: Path
    ) -> Path:
        self.logger.debug(f'Resolving subproject pointer: {subproject_pointer}')

        if subproject_pointer.find('://') >= 0:
            subproject_pointer_parts = subproject_pointer.split('#', maxsplit=1)
            repo_url = subproject_pointer_parts[0]
            revision = None

            if len(subproject_pointer_parts) == 2:
                revision = subproject_pointer_parts[1]

            self.logger.debug(
                f'Subproject location is the remote repo: {repo_url}, revision: {revision}'
            )

            subproject_cached_dir_path = self._sync_repo(multiproject_dir_path, repo_url, revision)

        else:
            subproject_source_dir_path = Path(multiproject_dir_path / subproject_pointer).resolve()

            self.logger.debug(f'Subproject location is the local path: {subproject_source_dir_path}')

            subproject_cached_dir_path = (
                multiproject_dir_path /
                self._cache_dir_name /
                subproject_source_dir_path.name
            ).resolve()

            if (
                self._cache_dir_name in self.project_path.resolve().parts
                and
                subproject_cached_dir_path.exists()
            ):
                self.logger.debug('Subproject already copied into cache')

            else:
                self.logger.debug('Copying the subproject into cache')

                rmtree(subproject_cached_dir_path, ignore_errors=True)
                copytree(subproject_source_dir_path, subproject_cached_dir_path)

        self.logger.debug(f'Subproject stored in cache: {subproject_cached_dir_path}')

        return subproject_cached_dir_path

    def _sync_repo(
        self,
        multiproject_dir_path: Path,
        repo_url: str,
        revision: str or None = None
    ) -> Path:
        repo_dir_path = (
            multiproject_dir_path /
            self._cache_dir_name /
            repo_url.split('/')[-1].rsplit('.', maxsplit=1)[0]
        ).resolve()

        if (
            self._cache_dir_name in self.project_path.resolve().parts
            and
            repo_dir_path.exists()
        ):
            self.logger.debug('Repo already synchronized')

        else:
            self.logger.debug('Synchronizing repo')

            self.logger.debug(f'Repo URL: {repo_url}, revision: {revision}, local path: {repo_dir_path}')

            try:
                self.logger.debug(f'Cloning repo {repo_url} to {repo_dir_path}')

                run(
                    f'git clone {repo_url} {repo_dir_path}',
                    shell=True,
                    check=True,
                    stdout=PIPE,
                    stderr=STDOUT
                )

            except CalledProcessError as exception:
                if repo_dir_path.exists():
                    self.logger.debug('Repo already cloned; pulling from remote')

                    run(
                        'git pull',
                        cwd=repo_dir_path,
                        shell=True,
                        check=True,
                        stdout=PIPE,
                        stderr=STDOUT
                    )

            if revision:
                self.logger.debug(f'Checking out to revision: {revision}')

                run(
                    f'git checkout {revision}',
                    cwd=repo_dir_path,
                    shell=True,
                    check=True,
                    stdout=PIPE,
                    stderr=STDOUT
                )

            self.logger.debug('Updating submodules')

            run(
                'git submodule update --init',
                cwd=repo_dir_path,
                shell=True,
                check=True,
                stdout=PIPE,
                stderr=STDOUT
            )

        return repo_dir_path

    def _get_chapters_with_overwritten_paths(
        self,
        chapters: dict,
        subproject_cached_dir_path: Path
    ) -> dict:
        self.logger.debug('Overwriting paths of chapters')

        subproject_cached_dir_name = subproject_cached_dir_path.name

        self.logger.debug(f'Cached subproject directory name: {subproject_cached_dir_name}')

        def _process_chapters(chapters_subset, subproject_cached_dir_name):
            if isinstance(chapters_subset, dict):
                new_chapters_subset = {}
                for key, value in chapters_subset.items():
                    new_chapters_subset[key] = _process_chapters(value, subproject_cached_dir_name)

            elif isinstance(chapters_subset, list):
                new_chapters_subset = []
                for item in chapters_subset:
                    new_chapters_subset.append(_process_chapters(item, subproject_cached_dir_name))

            elif isinstance(chapters_subset, str):
                if chapters_subset.endswith('.md'):
                    new_chapters_subset = f'{subproject_cached_dir_name}/{chapters_subset}'

                else:
                    new_chapters_subset = chapters_subset

            else:
                new_chapters_subset = chapters_subset

            return new_chapters_subset

        new_chapters = _process_chapters(chapters, subproject_cached_dir_name)

        self.logger.debug(f'Chapters with overwritten paths: {new_chapters}')

        return new_chapters
