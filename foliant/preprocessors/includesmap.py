'''
Preprocessor for Foliant.

Allows to merge includes maps.
'''

import json
from pathlib import Path

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.multiproject_includes_map = []

        self.logger = self.logger.getChild('includesmap')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def apply(self):
        self.logger.info('Applying preprocessor')

        for map in self.working_dir.rglob('includes_map.json'):
            path = map.relative_to(self.working_dir)
            with open(map, encoding='utf8') as f:
                data = f.read()

            if data:
                dir = path.parent
                if dir != Path("static"):
                    dir = dir.parent
                obj = json.loads(data)
                self.multiproject_includes_map.append({f"{dir.as_posix()}": obj})

        Path(f'{self.working_dir}/static/').mkdir(parents=True, exist_ok=True)
        with open(f'{self.working_dir}/static/multiproject_includes_map.json', 'w', encoding='utf8') as f:
            json.dump(self.multiproject_includes_map, f)
