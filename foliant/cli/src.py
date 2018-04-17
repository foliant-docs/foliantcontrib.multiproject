'''CLI extension for the ``src`` command.'''

from shutil import move, copytree, rmtree
from pathlib import Path
from importlib import import_module
from cliar import Cliar, set_metavars, set_help
from foliant.config import Parser


class Cli(Cliar):
    @set_metavars({'action': 'ACTION'})
    @set_help({'action': 'Action: backup, restore'})
    def src(self, action):
        '''Apply ACTION to the project directory.'''

        src_dir_path = Path(Parser(Path('.'), self.config_file_name)._get_multiproject_config()['src_dir']).expanduser()
        src_backup_dir_path = Path('__src_backup__')

        if action == 'backup':
            rmtree(src_backup_dir_path, ignore_errors=True)
            copytree(src_dir_path, src_backup_dir_path)
        elif action == 'restore':
            rmtree(src_dir_path, ignore_errors=True)
            move(src_backup_dir_path, src_dir_path)
        else:
            print("Unrecognized ACTION.")
            exit(1)
