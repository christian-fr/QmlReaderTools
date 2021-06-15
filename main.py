__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "1.0.13"
__status__ = "Prototype"
__name__ = "QmlReader_GUI"

# last edited 2020-04-01

import os
import shutil
from gui import mainInterface
from tkinter import Tk
from configparser import ConfigParser
from pathlib import Path
from typing import Union

local_dir = os.path.dirname(__file__)
abs_dir = os.path.join(os.getcwd(), local_dir)


class AdvancedConfig(ConfigParser):
    def __init__(self, set_config_path: Union[str, Path], set_config_template_path: Union[str, Path]):
        super().__init__()
        self.config_path = Path(set_config_path)
        self.config_template_path = Path(set_config_template_path)

    def initialize_config(self):
        shutil.copy(self.config_template_path, self.config_path)
        self.read(self.config_path)
        if 'paths' not in self.keys():
            self.add_section('paths')
        self.set('paths', 'home', Path.home().as_posix())
        self.set('paths', 'workspace', Path(Path.home(), 'zofar_workspace').as_posix())
        self.set('paths', 'faust_out', Path(Path.home(), r'\\faust\GPD-Transfer\friedrich\Out_'+os.path.split(Path.home())[1]).as_posix())
        self.write_config()


    def read_config(self):
        # copy template if config file does not yet exist
        if not self.config_path.exists():
            self.initialize_config()
        # read config file
        self.read(self.config_path)


    def write_config(self):
        with open(self.config_path, 'w') as f:
            self.write(f)


config_path = Path(abs_dir, 'config', 'config.ini')
config_template_path = Path(abs_dir, 'config', 'config.template')

config = AdvancedConfig(set_config_path=config_path, set_config_template_path=config_template_path)
config.read_config()

root = Tk()
app = mainInterface.Window(master=root, config_object=config)
root.wm_title("QML Reader " + str(__version__))
root.geometry('800x600')
root.mainloop()
