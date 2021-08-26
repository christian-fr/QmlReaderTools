__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "1.0.14"
__status__ = "Prototype"
__name__ = "QmlReader_GUI"

import os
import shutil
from gui import mainInterface
from tkinter import Tk
from configparser import ConfigParser
from pathlib import Path
from typing import Union
import argparse

local_dir = os.path.dirname(__file__)
abs_dir = os.path.join(os.getcwd(), local_dir)


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(f'The given startup argument is not a directory: "{string}"')


def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(f'The given startup argument is not a file: "{string}"')


parser = argparse.ArgumentParser(description='QmlReaderTools -- Optionally give a path to a QML/XML file or '
                                             'set the debug flag for verbose output and '
                                             'debug logging.',
                                 prog='main.py')

parser.add_argument('--debug', action='store_true', help='enable verbose output and debug logging')

subparsers = parser.add_subparsers(help='Load a file or a directory.')

# create the parser for the "file" command
parser_file = subparsers.add_parser('file', help='Load a file')
parser_file.add_argument('--infile', '-i', type=file_path, help='Input file path.')

# create the parser for the "directory" command
parser_directory = subparsers.add_parser('directory', help='Load a directory')
parser_directory.add_argument('--indirectory', '-i', type=dir_path, help='Input directory path.')

args = parser.parse_args()

# assert that optional debug flag is of boolean type
assert isinstance(args.debug, bool)
# set flag for debug
flag_debug = args.debug


class AdvancedConfig(ConfigParser):
    def __init__(self, set_config_path: Union[str, Path], set_config_file_name: Union[str, Path],
                 set_config_template_path: Union[str, Path]):
        super().__init__()
        self.config_path = Path(set_config_path)

        # set full path of config file
        self.config_file_full_path = Path(self.config_path, set_config_file_name)

        self.config_template_path = Path(set_config_template_path)

        if not self.config_file_full_path.exists():
            self.initialize_config()

        self.read_config()
        print('')

    def initialize_config(self):
        # create config dir if it not yet exists
        os.makedirs(self.config_path, exist_ok=True)

        shutil.copy(self.config_template_path, self.config_file_full_path)

        self.read(self.config_file_full_path, encoding='utf-8')
        if 'paths' not in self.keys():
            self.add_section('paths')
        self.set('paths', 'home', Path.home().as_posix())
        self.set('paths', 'workspace', Path.home().as_posix())
        self.set('paths', 'output_path', Path.home().as_posix())
        self.write_config()

    def read_config(self):
        # read config file
        self.read(self.config_file_full_path, encoding='utf-8')

    def write_config(self):
        # used "with ... as:" instead of "Path(...).write_text(...)" because self.write is a native method of ConfigParser
        with open(str(self.config_file_full_path), 'w', encoding='utf-8') as f:
            self.write(f)


config_path = Path(os.path.join(os.path.expanduser('~'), '.qmlreadertools'))
config_file = 'qmlreadertools.ini'
config_template_path = Path(local_dir, 'config', 'config.template')

config = AdvancedConfig(set_config_path=config_path,
                        set_config_file_name='qmlreadertools.ini',
                        set_config_template_path=config_template_path)

root = Tk()
app = mainInterface.Window(master=root, config_object=config, args_object=args)
root.wm_title("QML Reader " + str(__version__))
root.geometry('800x600')
root.mainloop()
