__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "0.3.5"
__status__ = "Prototype"
__name__ = "QmlReader_GUI"

from qmlReader import qmlReader, questionnaire
import tkinter
from tkinter import filedialog, scrolledtext, IntVar, messagebox
from os import listdir
import os.path
import logging
import configparser
import argparse
from typing import Union, Optional
from pathlib import Path
from collections import defaultdict


class QmlDetails(dict):
    def __init__(self):
        super(QmlDetails, self).__init__()

    def __str__(self):
        tmp_str = ''
        for key, val in self.items():
            tmp_str += '\n\n'
            tmp_str += '### ' + str(key) + '\n\n'
            tmp_str += str(val)
        return tmp_str


class Window(tkinter.Frame):
    """
    main application
    """

    def __init__(self, config_object: "AdvancedConfig", args_object: argparse.Namespace, master=None):
        self.window_selection = None
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)

        self.logger.info('starting up')
        tkinter.Frame.__init__(self, master)
        self.dict_of_questionnaires = {}
        # self.questionnaire = Questionnaire.Questionnaire()
        self.master = master
        self.dict_of_qmls = {}
        self.questionnaire_combined = questionnaire.Questionnaire()
        self.listOfFiles = []
        self.listOfFilesFull = []
        self.list_of_selected_files = []
        menu = tkinter.Menu(self.master)
        self.master.config(menu=menu)

        # initialize initial directory and file
        self.initial_directory_to_load, self.initial_file_to_load = None, None
        # set initial directory and file
        if hasattr(args_object, 'indirectory'):
            self.initial_directory_to_load = args_object.indirectory
        if hasattr(args_object, 'infile'):
            self.initial_file_to_load = args_object.infile

        self.config = config_object

        file_menu = tkinter.Menu(menu, tearoff=False)
        file_menu.add_command(label="Import File", command=self.load_files)
        file_menu.add_command(label="Import Directory", command=self.load_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tkinter.Menu(menu, tearoff=False)
        edit_menu.add_command(label="placeholder")
        edit_menu.add_command(label="placeholder")
        menu.add_cascade(label="Edit", menu=edit_menu)

        self.fileNameText = '(no files selected)'
        self.dirText = '(no path selected)'

        self.labelPathInfo = tkinter.Label(self.master, text='Path:')
        self.labelPathInfo.grid(row=0, column=0, sticky='W')

        self.labelPath = tkinter.Label(self.master, text=' ' + self.dirText)
        self.labelPath.grid(row=1, column=0, sticky='W')

        self.labelFileInfo = tkinter.Label(self.master, text='Filename(s):')
        self.labelFileInfo.grid(row=2, column=0, sticky='W')

        self.text1 = scrolledtext.ScrolledText(self.master, width=60, height=25)
        self.text1.grid(row=3, column=0, sticky='W')
        self.text1.insert(tkinter.END, self.fileNameText)
        self.text1.config(state=tkinter.DISABLED)

        self.canvas1 = tkinter.Canvas(self.master, width=100, height=25)
        self.canvas1.grid(row=1, column=2, sticky='NW', rowspan=5, padx=12)
        self.__button_dict = {}

        self.button1 = tkinter.Button(self.canvas1, width=20, height=1, text='Read QML(s)', state=tkinter.DISABLED,
                                      command=self.run_qml_reader)
        self.button1.grid(row=1, column=2, sticky='N')
        self.__button_dict['read_qml'] = self.button1

        self.button2 = tkinter.Button(self.canvas1, width=20, height=1, text='Combine QMLs', state=tkinter.DISABLED,
                                      command=self.run_combine_questionnaires)
        self.button2.grid(row=2, column=2, sticky='N')
        self.__button_dict['combine'] = self.button2

        self.button3 = tkinter.Button(self.canvas1, width=20, height=1, text='QML Details', state=tkinter.DISABLED,
                                      command=self.run_qml_details_dialogue)
        self.button3.grid(row=3, column=2, sticky='N')
        self.__button_dict['qml_details'] = self.button3

        self.button4 = tkinter.Button(self.canvas1, width=20, height=1, text='Page Details', state=tkinter.DISABLED,
                                      command=self.run_show_page_details_dialogue)
        self.button4.grid(row=4, column=2, sticky='N')
        self.__button_dict['page_details'] = self.button4

        self.button5 = tkinter.Button(self.canvas1, width=20, height=1, text='Flowchart', state=tkinter.DISABLED,
                                      command=self.run_flowchart_dialog)
        self.button5.grid(row=5, column=2, sticky='N')
        self.__button_dict['flowchart'] = self.button5

        self.button6 = tkinter.Button(self.canvas1, width=20, height=1, text='weighted Flowchart',
                                      state=tkinter.DISABLED)
        self.button6.grid(row=6, column=2, sticky='N')
        self.__button_dict['weighted_flowchart'] = self.button6

        self.button7 = tkinter.Button(self.canvas1, width=20, height=1, text='', state=tkinter.DISABLED)
        self.button7.grid(row=7, column=2, sticky='N')
        self.__button_dict['btn7'] = self.button7

        self.button8 = tkinter.Button(self.canvas1, width=20, height=1, text='', state=tkinter.DISABLED)
        self.button8.grid(row=8, column=2, sticky='N')
        self.__button_dict['btn8'] = self.button8

        self.button9 = tkinter.Button(self.canvas1, width=20, height=1, text='', state=tkinter.DISABLED)
        self.button9.grid(row=9, column=2, sticky='N')
        self.__button_dict['btn9'] = self.button8

        self.button10 = tkinter.Button(self.canvas1, width=20, height=1, text='Open Path', state=tkinter.DISABLED,
                                       command=self.open_path)
        self.button10.grid(row=7, column=2, sticky='N')
        self.__button_dict['open_path'] = self.button10

        if self.initial_file_to_load:
            self.load_files(initial_file=self.initial_file_to_load)
        elif self.initial_directory_to_load:
            self.load_dir(initial_dir=self.initial_directory_to_load)

        if self.initial_file_to_load or self.initial_directory_to_load:
            self.run_qml_reader()

    def open_path(self):
        path = os.path.realpath(self.dirText)
        os.system(f'pcmanfm {os.path.realpath(path)}')

    def deactivate_all_buttons(self):
        self.activate_button(self.__button_dict.keys(), deactivate=True)

    def activate_all_buttons(self):
        self.activate_button(self.__button_dict.keys())

    def activate_button(self, button_name_list_of_strings, deactivate=False):
        '''
        :param button_name_list_of_strings: list of strings - button names; has to correspond to the keys of self.__button_dict
        :param deactivate: False is default; if True: deactivates Buttons in argument list
        :return: no return
        '''
        self.logger.info(
            'de-/activating buttons: ' + str(button_name_list_of_strings) + ', deactivate=' + str(deactivate))
        try:
            assert isinstance(button_name_list_of_strings, list)
        except AssertionError:
            print('Argument passed: "' + str(button_name_list_of_strings) + '"\n was not a list of strings!')
            self.logger.error(
                'Argument passed: "' + str(button_name_list_of_strings) + '"\n was not a list of strings!')
        for entry_str in button_name_list_of_strings:
            self.check_entry_buttonlist_if_string(entry_str)
            self.check_entry_buttonlist_if_in_dict(entry_str)
        if deactivate is True:
            for entry_str in button_name_list_of_strings:
                self.__button_dict[entry_str].config(state=tkinter.DISABLED)
        else:
            for entry_str in button_name_list_of_strings:
                self.__button_dict[entry_str].config(state=tkinter.NORMAL)

    def check_entry_buttonlist_if_string(self, entry):
        try:
            assert isinstance(entry, str)
        except AssertionError:
            self.logger.exception(
                'The argument list contains an element that is not a string!\n argument reads: "' + str(
                    entry) + '" and is of type: "' + str(type(entry)) + '"')
            print(
                'The argument list contains an element that is not a string!\n argument reads: "' + str(
                    entry) + '" and is of type: "' + str(type(entry)) + '"')

    def check_entry_buttonlist_if_in_dict(self, entry_str):
        try:
            assert entry_str in self.__button_dict
        except AssertionError:
            self.logger.exception('Button name ' + entry_str + 'not found in self.__button_dict!')
            print('Button name ' + entry_str + 'not found in self.__button_dict!')

    @staticmethod
    def exit_program():
        exit()

    def redraw_file_text(self):
        self.update()
        print(self.listOfFiles)
        self.text1.config(state=tkinter.NORMAL)
        self.text1.delete('1.0', tkinter.END)
        if len(self.listOfFiles) == 0:
            self.fileNameText = ' --> no *.xml-files found in this path!'
            self.deactivate_all_buttons()
            self.no_files_selected()
        else:
            self.fileNameText = '\n'.join(self.listOfFiles)
            self.activate_button(['read_qml'])
        self.text1.insert('1.0', self.fileNameText)
        self.text1.config(state=tkinter.DISABLED)

    def redraw_path_label(self):
        self.update()
        self.labelPath.destroy()
        self.labelPath = tkinter.Label(self.master, text=' ' + self.dirText)
        self.labelPath.grid(row=1, column=0, sticky='W')

    def no_files_selected(self):
        self.deactivate_all_buttons()

    @staticmethod
    def sort_list_of_files(temp_files):
        temp_files.sort()
        return temp_files

    def load_files(self,
                   filetypes=(("xml files", "*.xml"), ("all files", "*.*")),
                   initial_file: Union[Path, str, None] = None):
        if initial_file:
            temp_files = [initial_file]
        else:
            temp_files = self.open_files(filetypes=filetypes)

        self.logger.info('opening files: ' + str(temp_files))
        if len(temp_files) == 0:
            return
        try:
            assert isinstance(temp_files, list)
        except AssertionError:
            self.logger.exception(
                'Assertion error: ' + str(temp_files) + ' \nis not a list, but of type: ' + str(type(temp_files)))
        temp_files = self.sort_list_of_files(temp_files)
        self.listOfFilesFull = temp_files
        self.listOfFiles = [os.path.split(f)[1] for f in temp_files]
        if len(temp_files) == 0:
            self.dirText = '(no path selected)'
        else:
            self.dirText = os.path.split(temp_files[0])[0]
        print(self.listOfFiles)
        self.redraw_path_label()
        self.redraw_file_text()

    def open_files(self, filetypes):
        self.logger.info('starting file dialog askopenfilenames')
        tmp_path_list = list(
            filedialog.askopenfilenames(filetypes=filetypes,
                                        initialdir=self.config.get('paths', 'workspace')))
        if tmp_path_list:
            tmp_workspace_path = tmp_path_list[0]
            if Path(tmp_path_list[0]).is_file():
                tmp_workspace_path = os.path.split(tmp_workspace_path)[0]
            self.config.set('paths', 'workspace', tmp_workspace_path)
            self.config.write_config()
        return tmp_path_list

    def open_dir(self):
        self.logger.info('starting file dialog askdirectory')
        tmp_workspace_path = filedialog.askdirectory()
        self.config.set('paths', 'workspace', tmp_workspace_path)
        self.config.write_config()
        return

    def load_dir(self, initial_dir: Union[Path, str, None] = None):
        if initial_dir:
            selected_path = initial_dir
        else:
            selected_path = self.open_dir()
        self.logger.info('selected path: ' + str(selected_path))
        if len(selected_path) == 0:
            return
        self.dirText = selected_path
        only_files = [f for f in listdir(selected_path) if
                      os.path.isfile(os.path.join(selected_path, f)) and
                      os.path.splitext(f)[1] == '.xml' and
                      os.path.split(f)[1].find('questionnaire') == 0]
        self.logger.info('list of files from directory: ' + str(only_files))
        try:
            assert isinstance(only_files, list)
        except AssertionError:
            self.logger.exception(
                'Assertion error: ' + str(only_files) + ' \nis not a list, but of type: ' + str(type(only_files)))
        only_files.sort()

        self.listOfFiles = only_files
        self.listOfFilesFull = [os.path.join(selected_path, f) for f in only_files]

        self.redraw_path_label()
        self.redraw_file_text()

    def run_qml_reader(self):
        print("run_qml_reader")
        self.dict_of_qmls = {}
        if self.listOfFilesFull is []:
            return
        for entry in self.listOfFilesFull:
            print(entry)
            self.dict_of_qmls[os.path.split(entry)[1]] = qmlReader.QmlReader(entry)

        for key in self.dict_of_qmls:
            self.read_into_questionnaire_objects(key=key)

        self.activate_button(['qml_details', 'combine', 'flowchart', 'open_path'])

    def run_combine_questionnaires(self):
        print("run_combine_questionnaires")
        self.questionnaire_combined = questionnaire.Questionnaire()
        self.selection_dialogue('combine')

    def read_into_questionnaire_objects(self, key):
        self.dict_of_questionnaires = {}
        for page in self.dict_of_qmls[key].list_of_pages():
            for key in self.dict_of_qmls:
                self.dict_of_questionnaires[key] = self.dict_of_qmls[key].questionnaire

    # def read_into_page_objects(self, key_page, page):
    #             string_pagename = key_page
    #             dict_of_transitions = self.dict_of_qmls[key_page].dict_of_transitions[page]
    #             dict_of_sources = self.dict_of_qmls[key_page].dict_of_sources[page]
    #             list_of_variables = None
    #             question_string = None
    #             instruction_string = None
    #             title_string = None
    #             temp_page = Questionnaire.QmlPage(string_pagename=string_pagename,
    #                                               dict_of_transitions=dict_of_transitions,
    #                                               dict_of_sources=dict_of_sources,
    #                                               list_of_variables=list_of_variables,
    #                                               question_string=question_string,
    #                                               instruction_string=instruction_string,
    #                                               title_string=title_string)
    #
    #             self.dict_of_questionnaires[key_page].add_page(temp_page)
    #

    def run_qml_details_dialogue(self):
        self.selection_dialogue('details')

    def run_flowchart_dialog(self):
        self.selection_dialogue('flowchart')

    def selection_dialogue(self, action):
        self.window_selection = tkinter.Toplevel(self)
        self.window_selection.wm_title("XML selection")
        self.window_selection.geometry('800x600')

        self.window_selection.canvas1 = tkinter.Canvas(self.window_selection, width=300, height=25)
        self.window_selection.canvas1.grid(row=0, column=0, sticky='NW', rowspan=25, padx=0)

        self.window_selection.canvas2 = tkinter.Canvas(self.window_selection, width=300, height=25)
        self.window_selection.canvas2.grid(row=0, column=1, sticky='NE', rowspan=25, padx=0)
        self.window_selection.checkbox_list = [list() for i in range(0, len(self.listOfFilesFull))]

        self.window_selection.dict_of_vars = {}  # dict of {index_int: (fullpath_str, checkboxvalue_int)}
        for i in range(0, len(self.listOfFilesFull)):
            self.window_selection.dict_of_vars[i] = tuple([self.listOfFilesFull[i], IntVar()])
            self.window_selection.checkbox_list[i] = tkinter.Checkbutton(self.window_selection.canvas1,
                                                                         text=os.path.split(self.listOfFilesFull[i])[1],
                                                                         variable=self.window_selection.dict_of_vars[i][
                                                                             1],
                                                                         onvalue=1, offvalue=0)
            self.window_selection.checkbox_list[i].grid(row=i, column=0, sticky='NW', padx=0)
            self.window_selection.checkbox_list[i].select()

        if action == 'details':
            self.window_selection.button1 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='Show details', state=tkinter.NORMAL,
                                                           command=self.action_details_show)

            self.window_selection.button2 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button3 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button4 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button5 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button6 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

        if action == 'flowchart':
            self.window_selection.button1 = tkinter.Button(self.window_selection.canvas2, width=20, height=2,
                                                           text='Flowchart(s)\nw/ var & cond', state=tkinter.NORMAL,
                                                           command=self.action_delay_flowchart_creation_show_var_show_cond_create_biderectional)

            self.window_selection.button2 = tkinter.Button(self.window_selection.canvas2, width=20, height=2,
                                                           text='Flowchart(s)\nw/o var, w/ cond', state=tkinter.NORMAL,
                                                           command=self.action_delay_flowchart_creation_omit_var_show_cond_no_biderectional)

            self.window_selection.button3 = tkinter.Button(self.window_selection.canvas2, width=20, height=2,
                                                           text='Flowchart(s)\nw/o var & cond', state=tkinter.NORMAL,
                                                           command=self.action_delay_flowchart_creation_omit_var_omit_cond_no_biderectional)

            self.window_selection.button4 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button5 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button6 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

        if action == 'combine':
            self.window_selection.button1 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='Combine QMLs', state=tkinter.NORMAL,
                                                           command=self.action_combine_questionnaires)

            self.window_selection.button2 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button3 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button4 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button5 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

            self.window_selection.button6 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='--', state=tkinter.NORMAL,
                                                           command=None)

        self.window_selection.button7 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                       text='Close', state=tkinter.NORMAL,
                                                       command=self.window_selection.destroy)
        self.window_selection.button1.grid(row=0, column=2, padx=0, sticky='NE')
        self.window_selection.button2.grid(row=1, column=2, padx=0, sticky='NE')
        self.window_selection.button3.grid(row=2, column=2, padx=0, sticky='NE')
        self.window_selection.button4.grid(row=3, column=2, padx=0, sticky='NE')
        self.window_selection.button5.grid(row=4, column=2, padx=0, sticky='NE')
        self.window_selection.button6.grid(row=5, column=2, padx=0, sticky='NE')
        self.window_selection.button7.grid(row=6, column=2, padx=0, sticky='NE')

    @staticmethod
    def do_nothing():
        pass

    def action_delay_flowchart_creation_show_var_show_cond_create_biderectional(self):
        self.action_flowchart_create(show_conditions=True, show_varnames=True, create_biderectional_edges=False)

    def action_delay_flowchart_creation_omit_var_show_cond_no_biderectional(self):
        self.action_flowchart_create(show_conditions=True, show_varnames=False, create_biderectional_edges=False)

    def action_delay_flowchart_creation_omit_var_omit_cond_no_biderectional(self):
        self.action_flowchart_create(show_conditions=False, show_varnames=False, create_biderectional_edges=False)

    def action_combine_questionnaires(self):
        self.logger.info('clicked on "combine"')
        self.logger.info('list of filenames from selection: ' + str(self.list_of_filenames_from_selection()))
        temp_list = [os.path.split(path)[1] for path in self.list_of_selected_files]

        first = True
        for key in temp_list:
            if first is True:
                self.questionnaire_combined.file = self.dict_of_qmls[key].file
                first = False
        for key in self.dict_of_qmls.keys():
            self.questionnaire_combined.append_other_questionnaire(self.dict_of_qmls[key].questionnaire)
        tkinter.messagebox.showinfo('Success: questionnaires have been combined.')
        self.window_selection.destroy()

        # ToDo: fix this dirty, dirty workaround...
        self.dict_of_qmls['questionnaire_combined'] = self.dict_of_qmls[list(self.dict_of_qmls.keys())[0]]
        self.dict_of_qmls['questionnaire_combined'].questionnaire = self.questionnaire_combined
        self.dict_of_questionnaires['questionnaire_combined'] = self.questionnaire_combined
        self.listOfFilesFull.append('questionnaire_combined')
        self.listOfFiles = [os.path.split(f)[1] for f in self.listOfFilesFull]
        self.redraw_file_text()

    def action_flowchart_create(self, show_varnames=True, show_conditions=True, create_biderectional_edges=False):
        self.logger.info('clicked on "flowchart"')
        output_dir = self.open_dir()
        self.logger.info(f'output_dir: "{output_dir}"')
        self.logger.info('list of filenames from selection: ' + str(self.list_of_filenames_from_selection()))
        temp_list = [os.path.split(path)[1] for path in self.list_of_selected_files]
        if not show_varnames:
            [self.__flowcharts_omit_varnames(key) for key in temp_list]
        if not show_conditions:
            [self.__flowcharts_omit_conditions(key) for key in temp_list]
        if create_biderectional_edges:
            [self.__flowcharts_create_bidirectional_edges(key) for key in temp_list]

        [self.prepare_flowcharts(key=key, output_dir=output_dir) for key in temp_list]
        count = len(self.list_of_selected_files)
        if count == 1:
            tkinter.messagebox.showinfo('Success', str(count) + ' flowchart has been created.')
        if count > 1:
            tkinter.messagebox.showinfo('Success', str(count) + ' flowcharts have been created.')
        self.activate_button(['weighted_flowchart'])
        # self.window_selection.destroy()

    def prepare_flowcharts(self, key, output_dir=None):
        self.dict_of_questionnaires[key].transitions_to_nodes_edges(truncate=False)
        self.dict_of_questionnaires[key].flowchart_create_graph(output_dir=output_dir)

    def __flowcharts_omit_varnames(self, key):
        self.dict_of_questionnaires[key].flowchart_set_show_variablenames(False)

    def __flowcharts_omit_conditions(self, key):
        self.dict_of_questionnaires[key].flowchart_set_show_conditions(False)

    def __flowcharts_create_bidirectional_edges(self, key):
        self.dict_of_questionnaires[key].flowchart_set_bidirectional(True)

    def list_of_filenames_from_selection(self):
        local_list = [self.window_selection.dict_of_vars[i][0] for i in self.window_selection.dict_of_vars if
                      self.window_selection.dict_of_vars[i][1].get() == 1]
        self.logger.info('List of filenames from checkboxes created: ' + str(local_list))
        print('List of filenames from checkboxes created: ' + str(local_list))
        self.list_of_selected_files = local_list
        self.window_selection.details_string_dict = self.details_preparation(local_list)

    def action_details_show(self):
        self.logger.info('clicked on "details"')
        self.list_of_filenames_from_selection()

        for checkbox in self.window_selection.checkbox_list:
            checkbox.destroy()
        self.window_selection.button1.config(state=tkinter.DISABLED)
        self.window_selection.button3 = tkinter.Button(self.window_selection.canvas2, width=10, height=2,
                                                       text='Save as...', state=tkinter.NORMAL,
                                                       command=self.details_write_file)
        self.window_selection.button3.grid(row=0, column=2, padx=0, pady=0, sticky='NE')

        self.window_selection.button4 = tkinter.Button(self.window_selection.canvas2, width=10, height=2,
                                                       text='Save Stata\ntopologically', state=tkinter.NORMAL,
                                                       command=self.details_write_stata_topologically)
        self.window_selection.button4.grid(row=2, column=2, padx=0, pady=0, sticky='NE')

        self.window_selection.button5 = tkinter.Button(self.window_selection.canvas2, width=10, height=2,
                                                       text='Save Stata\ndeclared', state=tkinter.NORMAL,
                                                       command=self.details_write_stata_declared)
        self.window_selection.button5.grid(row=4, column=2, padx=0, pady=0, sticky='NE')

        self.window_selection.text1 = scrolledtext.ScrolledText(self.window_selection, width=80, height=25)
        self.window_selection.text1.grid(row=0, column=0, sticky='W')
        self.window_selection.text1.insert(tkinter.END, self.window_selection.details_string_dict)
        self.window_selection.text1.config(state=tkinter.NORMAL)

    def details_write_stata_topologically(self):
        self.logger.info('"save stata topologically" dialog starts')
        fullpath = tkinter.filedialog.asksaveasfilename(initialdir=self.config.get('paths', 'faust_out'),
                                                        defaultextension='.txt',
                                                        confirmoverwrite=True,
                                                        filetypes=[("Stata Do-Files", "*.do")],
                                                        initialfile='maxpage_.do')
        self.logger.info('chosen full path: ' + str(fullpath))
        with open(fullpath, 'w') as file:
            # ToDo 2021-06-15: needs fixing, does not yet save only the stata string to a file
            # ToDo 2021-06-15: needs restructuring, maybe a separate details class containing all relevant information that is stored within
            #  self.dict_of_questionnaires[questionnaire_filename].details
            # ToDo 2021-06-15: restructuring so that the output of multiple questionnaire details are possible (maybe subsequently, one askfilesave at a time
            file.writelines(self.window_selection.details_string_dict['stata_maxpage_topologically'])

    def details_write_stata_declared(self):
        pass

    # ToDo: disentangle from method "list_of_filenames_from_selection"
    def details_preparation(self, list_of_fullpaths):
        list_of_filenames = [os.path.split(file)[1] for file in list_of_fullpaths]

        tmp_return_string = ''
        for filename in list_of_filenames:
            details_object = self.details_prepare_from_qml(self.dict_of_qmls[filename])
            tmp_return_string += '\n\n###########################################\n\n'
            tmp_return_string += 'filename: ' + str(filename) + '\n\n' + str(details_object)

        # add details_object to questionnaire
        for filename in self.dict_of_questionnaires.keys():
            self.dict_of_questionnaires[filename].details = details_object

        return tmp_return_string

    def details_write_file(self):
        self.logger.info('"save as" dialog starts')
        fullpath = tkinter.filedialog.asksaveasfilename(defaultextension='.txt', confirmoverwrite=True)
        self.logger.info('chosen full path: ' + str(fullpath))
        with open(fullpath, 'w') as file:
            file.writelines(self.window_selection.details_string_dict)

    # ToDo (inherited from method "details_preparation"): disentangle from method "list_of_filenames_from_selection"
    def details_prepare_from_qml(self, qml_reader_object):
        """
        input: a single qml_reader_object
        :return: a string of details
        """

        details_object = QmlDetails()

        try:
            assert isinstance(qml_reader_object, qmlReader.QmlReader)
        except AssertionError:
            self.logger.exception(f'Wrong input type: "{type(qml_reader_object)}"')

        details_string = ''
        details_string += '\n### title:\n'
        details_string += str(qml_reader_object.title)

        details_object['title'] = str(qml_reader_object.title)

        details_string += '\n### list of pages: [' + str(
            len(qml_reader_object.questionnaire.pages.list_of_all_pagenames())) + ']\n'
        details_string += str(qml_reader_object.questionnaire.pages.list_of_all_pagenames())
        details_string += '\n\n'

        details_object[
            'number_of_pages'] = f'[{str(len(qml_reader_object.questionnaire.pages.list_of_all_pagenames()))}]'
        details_object['list_of_pages'] = str(qml_reader_object.questionnaire.pages.list_of_all_pagenames())

        details_string += '\n### topologically sorted list of pages:\n'
        tmp_list_of_topologically_sorted_pages = qml_reader_object.questionnaire.return_topologically_sorted_list_of_pages()
        if tmp_list_of_topologically_sorted_pages:
            details_string += str(tmp_list_of_topologically_sorted_pages)
        else:
            details_string += '!! Graph contains cycles and can therefore not be topologically sorted. !!'

        if tmp_list_of_topologically_sorted_pages:
            details_object['list_of_pages_topologically_sorted'] = str(
                qml_reader_object.questionnaire.return_topologically_sorted_list_of_pages())
        else:
            details_object['list_of_pages_topologically_sorted'] = None

        details_string += '\n\n'

        details_string += '\n### variables: [' + str(
            len(qml_reader_object.questionnaire.variables.list_all_vars())) + ']\n'
        details_string += str(qml_reader_object.questionnaire.variables.list_all_vars())
        details_string += '\n\n'

        details_object[
            'number_of_variables'] = f'[{str(len(qml_reader_object.questionnaire.variables.list_all_vars()))}]'
        details_object['list_of_variables'] = str(qml_reader_object.questionnaire.variables.list_all_vars())

        # ########################################################################
        # ToDo: everything else within this method should use the following form
        details_string += '\n\n### variable types: \n'

        details_object['list_of_variables_and_types'] = '\n'.join(
            [f'{key}\t{val.vartype}' for key, val in qml_reader_object.questionnaire.variables.variables.items()])

        details_string += details_object['list_of_variables_and_types']
        #
        # ########################################################################

        # ########################################################################
        # variables by type
        details_string += '\n\n### variables by type: \n'

        set_of_vartypes = set([val.vartype for val in qml_reader_object.questionnaire.variables.variables.values()])
        tmp_vartype_dict = defaultdict(list)
        for vartype in set_of_vartypes:
            tmp_vartype_dict[vartype] = [key for key, val in qml_reader_object.questionnaire.variables.variables.items()
                                         if
                                         val.vartype == vartype]

        details_object['list_of_variables_by_type'] = ''
        for key, val in tmp_vartype_dict.items():
            details_object['list_of_variables_by_type'] += f'{key}: {val}\n\n'
        # details_object['list_of_variables_by_type'] = '\n'.join(
        #     [f'{key}\t{val.vartype}' for key, val in qml_reader_object.questionnaire.variables.variables.items()])

        details_string += details_object['list_of_variables_by_type']
        #
        # ########################################################################

        details_string += '\n#### used variables per page:\n'

        details_object['used_variables_per_page'] = ''

        for page_name, page_object in qml_reader_object.questionnaire.pages.pages.items():
            details_string += f'{page_name}\t{[var_name for var_name in page_object.variables.variables.keys()]}\n'
            details_object[
                'used_variables_per_page'] += f'{page_name}\t{[var_name for var_name in page_object.variables.variables.keys()]}\n'

        # details_string_dict += '\nvariables extracted from declaration: [' + str(
        #     len(qml_reader_object.list_of_variables_from_declaration())) + ']\n'
        # details_string_dict += str(qml_reader_object.list_of_variables_from_declaration())
        # details_string_dict += '\n\n'

        tmp_list_unused_variables = qml_reader_object.questionnaire.find_unused_variables()
        details_string += '\n### unused variables:  [' + str(len(tmp_list_unused_variables)) + ']\n'
        details_string += str(tmp_list_unused_variables)
        details_string += '\n\n'

        details_object['unused_variables'] = str(tmp_list_unused_variables)

        details_string += f'\n### variables declaration, ordered and commented\n'
        details_string += '\n\n'

        tmp_str_variables_declaration_ordered_and_commented = ''
        tmp_list_of_already_declared_varnames = []
        for page_name, page_object in qml_reader_object.questionnaire.pages.pages.items():
            tmp_str_variables_declaration_ordered_and_commented += f'\n<!-- {page_name} -->\n'
            for var_name, variable_object in sorted(page_object.variables.variables.items()):
                if var_name not in tmp_list_of_already_declared_varnames:
                    tmp_str_variables_declaration_ordered_and_commented += f'\t\t <zofar:variable name="{var_name}" type="{variable_object.vartype}"/>\n'
                    tmp_list_of_already_declared_varnames.append(var_name)

        details_string += tmp_str_variables_declaration_ordered_and_commented

        details_object[
            'variables_declaration_ordered_and_commented'] = tmp_str_variables_declaration_ordered_and_commented

        details_object['shown_variables_per_page'] = ''
        details_string += '\n### shown variables per page:\n'
        for pagename, page_object in qml_reader_object.questionnaire.pages.pages.items():
            if page_object.variables.list_all_shown_vars():
                details_string += f'{pagename}\t{page_object.variables.list_all_shown_vars()}\n'
                details_object[
                    'shown_variables_per_page'] += f'{pagename}\t{page_object.variables.list_all_shown_vars()}\n'

        tmp_list_of_all_transitions = qml_reader_object.questionnaire.return_list_of_transitions(min_distance=None,
                                                                                                 max_distance=None,
                                                                                                 max_count=None)

        details_string += f'\n### list of all transitions: [{str(len(tmp_list_of_all_transitions))}]\n'
        details_object['list_of_all_transitions'] = ''
        for entry in tmp_list_of_all_transitions:
            details_string += str(entry) + '\t' + str(entry.condition) + '\n'
            details_object['list_of_all_transitions'] += str(entry) + '\t' + str(entry.condition) + '\n'

        details_object['len_list_of_all_transitions'] = str(len(tmp_list_of_all_transitions))

        # details_string_dict += '\npages declared in data_qml:  ['+ str(len(set(qml_reader_object.list_of_pages_declared))) + ']\n'
        # details_string_dict += str(set(qml_reader_object.list_of_pages_declared))
        # details_string_dict += '\n\n'
        # details_string_dict += '\npages not declared in data_qml, but mentioned in transitions:  [' + str(len(set(qml_reader_object.list_of_pages_not_declared_but_in_transitions))) + ']\n'
        # details_string_dict += str(set(qml_reader_object.list_of_pages_not_declared_but_in_transitions))

        details_object['stata_maxpage_topologically'] = '### STATA code for maxpage (topologically sorted):\n'
        details_string += '\n### STATA code for maxpage (topologically sorted):\n'

        details_string += '''*********************************************************************\n*_______________ XXXXX BEFRAGUNG (JAHR) ___________\nglobal version "XXXXX JAHR-MONAT-TAG"\nglobal workdir "XXXXX P:\\Zofar\\Promoviertenpanel\\ORDNER\\"	\nglobal orig "XXXXX ${workdir}orig\\${version}\\"\nglobal out "XXXXX ${workdir}\\lieferung\\BEFRAGUNG\\${version}\"\n\n//log using "${workdir}maxpage-aufbereitung.smcl", replace\ncd "${workdir}\\doc"\ncap log close\nlog using maxpage-aufbereitung_`: di %tdCY-N-D daily("$S_DATE", "DMY")', replace\n\n\n****************************************************************************\n** Projekt/ Studie: XXXXX BEFRAGUNG\n** Erstellung: XXXXX AUTOR*IN\n** Erstelldatum: XXXXX TAG.MONAT.JAHR\n** Rohdaten: history.csv \n** Datensatz-Ergebnis: \n************** XXXXX INPUT-DATEI\n** Log File:   maxpage-aufbereitung_.smcl\n*************************************************************************\nset more off					// Anzeige wird nicht unterbrochen\nclear						// löscht die Daten im Memory\n\n*________Rohdaten importieren___________________\nimport delimited "${orig}history.csv", clear\n\n*__________Fragebogenseiten nummerieren___________\n// Alle Seiten mit nichtnumerischer Bezeichnung (zusätzlich zu "index" und "end")\n// müssen manuell nachkodiert werden (siehe replace-command)\ngen pagenum=.\n'''
        details_object[
            'stata_maxpage_topologically'] += '''*********************************************************************\n*_______________ XXXXX BEFRAGUNG (JAHR) ___________\nglobal version "XXXXX JAHR-MONAT-TAG"\nglobal workdir "XXXXX P:\\Zofar\\Promoviertenpanel\\ORDNER\\"	\nglobal orig "XXXXX ${workdir}orig\\${version}\\"\nglobal out "XXXXX ${workdir}\\lieferung\\BEFRAGUNG\\${version}\"\n\n//log using "${workdir}maxpage-aufbereitung.smcl", replace\ncd "${workdir}\\doc"\ncap log close\nlog using maxpage-aufbereitung_`: di %tdCY-N-D daily("$S_DATE", "DMY")', replace\n\n\n****************************************************************************\n** Projekt/ Studie: XXXXX BEFRAGUNG\n** Erstellung: XXXXX AUTOR*IN\n** Erstelldatum: XXXXX TAG.MONAT.JAHR\n** Rohdaten: history.csv \n** Datensatz-Ergebnis: \n************** XXXXX INPUT-DATEI\n** Log File:   maxpage-aufbereitung_.smcl\n*************************************************************************\nset more off					// Anzeige wird nicht unterbrochen\nclear						// löscht die Daten im Memory\n\n*________Rohdaten importieren___________________\nimport delimited "${orig}history.csv", clear\n\n*__________Fragebogenseiten nummerieren___________\n// Alle Seiten mit nichtnumerischer Bezeichnung (zusätzlich zu "index" und "end")\n// müssen manuell nachkodiert werden (siehe replace-command)\ngen pagenum=.\n'''

        tmp_list_of_topologically_sorted_pages = qml_reader_object.questionnaire.return_topologically_sorted_list_of_pages()

        for entry in qml_reader_object.questionnaire.pages.return_list_of_pagenames_with_only_condition_false():
            if entry in tmp_list_of_topologically_sorted_pages:
                tmp_list_of_topologically_sorted_pages.remove(entry)

        if tmp_list_of_topologically_sorted_pages:
            for i in range(len(tmp_list_of_topologically_sorted_pages)):
                details_string += f'replace pagenum = {i} if page =="{tmp_list_of_topologically_sorted_pages[i]}"\n'
                details_object[
                    'stata_maxpage_topologically'] += f'replace pagenum = {i} if page =="{tmp_list_of_topologically_sorted_pages[i]}"\n'

            details_string += '\n\ntab pagenum, miss\nlabel var pagenum "Nummer der  Fragebogenseite"\n'
            details_object[
                'stata_maxpage_topologically'] += '\n\ntab pagenum, miss\nlabel var pagenum "Nummer der  Fragebogenseite"\n'

            details_string += 'label define pagenumlb '
            details_object['stata_maxpage_topologically'] += 'label define pagenumlb '

            for i in range(len(tmp_list_of_topologically_sorted_pages)):
                details_string += f' {i} "{tmp_list_of_topologically_sorted_pages[i]}"'
                details_object['stata_maxpage_topologically'] += f' {i} "{tmp_list_of_topologically_sorted_pages[i]}"'

            details_string += '\nlabel val pagenum pagenumlb\n'
            details_object['stata_maxpage_topologically'] += '\nlabel val pagenum pagenumlb\n'

            details_string += '*__________maximaler Fragebogenfortschritt___________\nsort participant_id id, stable\nbysort participant_id: egen maxpage = max(pagenum)\nlabel var maxpage "maximaler Fortschritt im Fragebogen"\n\n*________überflüssige Variablen löschen____________________\ndrop timestamp page\n\n\n*________Datensatz aggregieren____________________\n// maximaler Wert der Seitennummer, letzter Token, Mittelwert des maximalen Seitenfortschrittes\nsort id\ncollapse (last) token (max) pagenum (mean)  maxpage , by(participant_id)\n\ntab token if maxpage!=pagenum\nlabel val maxpage pagenumlb\ndrop pagenum\n\n\n*________Datensatz speichern____________________\nsave "XXXXX ${out}csv\\OUTPUT_DATEI.dta", replace\n\nlog close'
            details_object[
                'stata_maxpage_topologically'] += '*__________maximaler Fragebogenfortschritt___________\nsort participant_id id, stable\nbysort participant_id: egen maxpage = max(pagenum)\nlabel var maxpage "maximaler Fortschritt im Fragebogen"\n\n*________überflüssige Variablen löschen____________________\ndrop timestamp page\n\n\n*________Datensatz aggregieren____________________\n// maximaler Wert der Seitennummer, letzter Token, Mittelwert des maximalen Seitenfortschrittes\nsort id\ncollapse (last) token (max) pagenum (mean)  maxpage , by(participant_id)\n\ntab token if maxpage!=pagenum\nlabel val maxpage pagenumlb\ndrop pagenum\n\n\n*________Datensatz speichern____________________\nsave "XXXXX ${out}csv\\OUTPUT_DATEI.dta", replace\n\nlog close'

        else:
            details_string += '!! Graph contains cycles and can therefore not be topologically sorted. !!'
            details_object[
                'stata_maxpage_topologically'] += '!! Graph contains cycles and can therefore not be topologically sorted. !!'

        details_string += '\n\n'

        details_string += '\n### STATA code for maxpage (sorted as declared in QML):\n'
        details_object['stata_maxpage_declared'] = '\n### STATA code for maxpage (sorted as declared in QML):\n'

        details_string += '''*********************************************************************\n*_______________ XXXXX BEFRAGUNG (JAHR) ___________\nglobal version "XXXXX JAHR-MONAT-TAG"\nglobal workdir "XXXXX P:\\Zofar\\Promoviertenpanel\\ORDNER\\"	\nglobal orig "XXXXX ${workdir}orig\\${version}\\"\nglobal out "XXXXX ${workdir}\\lieferung\\BEFRAGUNG\\${version}\"\n\n//log using "${workdir}maxpage-aufbereitung.smcl", replace\ncd "${workdir}\\doc"\ncap log close\nlog using maxpage-aufbereitung_`: di %tdCY-N-D daily("$S_DATE", "DMY")', replace\n\n\n****************************************************************************\n** Projekt/ Studie: XXXXX BEFRAGUNG\n** Erstellung: XXXXX AUTOR*IN\n** Erstelldatum: XXXXX TAG.MONAT.JAHR\n** Rohdaten: history.csv \n** Datensatz-Ergebnis: \n************** XXXXX INPUT-DATEI\n** Log File:   maxpage-aufbereitung_.smcl\n*************************************************************************\nset more off					// Anzeige wird nicht unterbrochen\nclear						// löscht die Daten im Memory\n\n*________Rohdaten importieren___________________\nimport delimited "${orig}history.csv", clear\n\n*__________Fragebogenseiten nummerieren___________\n// Alle Seiten mit nichtnumerischer Bezeichnung (zusätzlich zu "index" und "end")\n// müssen manuell nachkodiert werden (siehe replace-command)\ngen pagenum=.\n'''
        details_object[
            'stata_maxpage_declared'] += '''*********************************************************************\n*_______________ XXXXX BEFRAGUNG (JAHR) ___________\nglobal version "XXXXX JAHR-MONAT-TAG"\nglobal workdir "XXXXX P:\\Zofar\\Promoviertenpanel\\ORDNER\\"	\nglobal orig "XXXXX ${workdir}orig\\${version}\\"\nglobal out "XXXXX ${workdir}\\lieferung\\BEFRAGUNG\\${version}\"\n\n//log using "${workdir}maxpage-aufbereitung.smcl", replace\ncd "${workdir}\\doc"\ncap log close\nlog using maxpage-aufbereitung_`: di %tdCY-N-D daily("$S_DATE", "DMY")', replace\n\n\n****************************************************************************\n** Projekt/ Studie: XXXXX BEFRAGUNG\n** Erstellung: XXXXX AUTOR*IN\n** Erstelldatum: XXXXX TAG.MONAT.JAHR\n** Rohdaten: history.csv \n** Datensatz-Ergebnis: \n************** XXXXX INPUT-DATEI\n** Log File:   maxpage-aufbereitung_.smcl\n*************************************************************************\nset more off					// Anzeige wird nicht unterbrochen\nclear						// löscht die Daten im Memory\n\n*________Rohdaten importieren___________________\nimport delimited "${orig}history.csv", clear\n\n*__________Fragebogenseiten nummerieren___________\n// Alle Seiten mit nichtnumerischer Bezeichnung (zusätzlich zu "index" und "end")\n// müssen manuell nachkodiert werden (siehe replace-command)\ngen pagenum=.\n'''

        tmp_list_of_sorted_as_declared_pages = qml_reader_object.questionnaire.pages.list_of_all_pagenames()

        for entry in qml_reader_object.questionnaire.pages.return_list_of_pagenames_with_only_condition_false():
            if entry in tmp_list_of_sorted_as_declared_pages:
                tmp_list_of_sorted_as_declared_pages.remove(entry)

        for i in range(len(tmp_list_of_sorted_as_declared_pages)):
            details_string += f'replace pagenum = {i} if page =="{tmp_list_of_sorted_as_declared_pages[i]}"\n'
            details_object[
                'stata_maxpage_declared'] += f'replace pagenum = {i} if page =="{tmp_list_of_sorted_as_declared_pages[i]}"\n'

        details_string += 'label var pagenum "Nummer der Fragebogenseite"'
        details_object['stata_maxpage_declared'] += 'label var pagenum "Nummer der Fragebogenseite"'

        details_string += '\n\ntab pagenum, miss\nlabel var pagenum "Nummer der  Fragebogenseite"\n'
        details_object[
            'stata_maxpage_declared'] += '\n\ntab pagenum, miss\nlabel var pagenum "Nummer der  Fragebogenseite"\n'

        details_string += 'label define pagenumlb '
        details_object['stata_maxpage_declared'] += 'label define pagenumlb '

        for i in range(len(tmp_list_of_sorted_as_declared_pages)):
            details_string += f' {i} "{tmp_list_of_sorted_as_declared_pages[i]}"'
            details_object['stata_maxpage_declared'] += f' {i} "{tmp_list_of_sorted_as_declared_pages[i]}"'

        details_string += '\nlabel val pagenum pagenumlb\n'
        details_object['stata_maxpage_declared'] += '\nlabel val pagenum pagenumlb\n'

        details_string += '*__________maximaler Fragebogenfortschritt___________\nsort participant_id id, stable\nbysort participant_id: egen maxpage = max(pagenum)\nlabel var maxpage "maximaler Fortschritt im Fragebogen"\n\n*________überflüssige Variablen löschen____________________\ndrop timestamp page\n\n\n*________Datensatz aggregieren____________________\n// maximaler Wert der Seitennummer, letzter Token, Mittelwert des maximalen Seitenfortschrittes\nsort id\ncollapse (last) token (max) pagenum (mean)  maxpage , by(participant_id)\n\ntab token if maxpage!=pagenum\nlabel val maxpage pagenumlb\ndrop pagenum\n\n\n*________Datensatz speichern____________________\nsave "XXXXX ${out}csv\\OUTPUT_DATEI.dta", replace\n\nlog close'
        details_object[
            'stata_maxpage_declared'] += '*__________maximaler Fragebogenfortschritt___________\nsort participant_id id, stable\nbysort participant_id: egen maxpage = max(pagenum)\nlabel var maxpage "maximaler Fortschritt im Fragebogen"\n\n*________überflüssige Variablen löschen____________________\ndrop timestamp page\n\n\n*________Datensatz aggregieren____________________\n// maximaler Wert der Seitennummer, letzter Token, Mittelwert des maximalen Seitenfortschrittes\nsort id\ncollapse (last) token (max) pagenum (mean)  maxpage , by(participant_id)\n\ntab token if maxpage!=pagenum\nlabel val maxpage pagenumlb\ndrop pagenum\n\n\n*________Datensatz speichern____________________\nsave "XXXXX ${out}csv\\OUTPUT_DATEI.dta", replace\n\nlog close'

        # return details_string
        return details_object

    def run_show_page_details_dialogue(self):
        pass

    def run_find_variable_dialogue(self):
        pass

    def startup_logger(self, log_level=logging.DEBUG):
        """
        CRITICAL: 50, ERROR: 40, WARNING: 30, INFO: 20, DEBUG: 10, NOTSET: 0
        """
        logging.basicConfig(level=log_level)
        fh = logging.FileHandler("{0}.log".format('log_' + __name__))
        fh.setLevel(log_level)
        fh_format = logging.Formatter('%(name)s\t%(module)s\t%(funcName)s\t%(asctime)s\t%(lineno)d\t'
                                      '%(levelname)-8s\t%(message)s')
        fh.setFormatter(fh_format)
        self.logger.addHandler(fh)
