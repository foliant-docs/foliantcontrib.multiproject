'''CLI extension for the ``src`` command.'''

from shutil import move, copytree, rmtree
from pathlib import Path
from importlib import import_module
from logging import DEBUG, WARNING
from cliar import Cliar, set_arg_map, set_metavars, set_help
from foliant.config import Parser


class Cli(Cliar):
    @set_arg_map(
        {
            'project_dir_path': 'project-dir',
            'config_file_name': 'config',
        }
    )
    @set_metavars({'action': 'ACTION'})
    @set_help(
        {
            'action': 'Action: backup, restore',
            'project_dir_path': 'Path to the Foliant project',
            'config_file_name': 'Name of config file of the Foliant project',
            'debug': 'Log all events during build. If not set, only warnings and errors are logged'
        }
    )
    def src(self, action, project_dir_path=Path('.'), config_file_name='foliant.yml', debug=False):
        '''Apply ACTION to the project directory.'''

        self.logger.setLevel(DEBUG if debug else WARNING)

        self.logger.info('Processing started')

        self.logger.debug(
            f'Project directory path: {project_dir_path}, ' +
            f'config file name: {config_file_name}'
        )

        src_dir_path = Path(
            Parser(project_dir_path, config_file_name, self.logger)._get_multiproject_config()['src_dir']
        ).expanduser()

        src_backup_dir_path = project_dir_path / '__src_backup__'

        if action == 'backup':
            self.logger.debug('Backing up the source directory')

            rmtree(src_backup_dir_path, ignore_errors=True)
            copytree(src_dir_path, src_backup_dir_path)
        elif action == 'restore':
            self.logger.debug('Restoring the source directory')

            rmtree(src_dir_path, ignore_errors=True)
            move(src_backup_dir_path, src_dir_path)
        else:
            error_message = f'Unrecognized ACTION specified: {action}'

            self.logger.critical(error_message)

            raise RuntimeError(error_message)

        self.logger.info('Processing finished')
