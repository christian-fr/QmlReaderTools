__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "QmlReader_GUI"

import QmlReader
import Questionnaire
import tkinter
from tkinter import filedialog, scrolledtext, IntVar, messagebox
from os import listdir, mkdir
import os.path
import logging
import networkx as nx
import errno
import time


class Window(tkinter.Frame):
    """
    main application
    """

    def __init__(self, master=None):
        self.window_selection = None
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)

        self.logger.info('starting up')
        tkinter.Frame.__init__(self, master)
        self.dict_of_questionnaires = {}
        self.questionnaire = Questionnaire.Questionnaire()
        self.master = master
        self.dict_of_qmls = {}
        self.listOfFiles = []
        self.listOfFilesFull = []
        self.list_of_selected_files = []
        menu = tkinter.Menu(self.master)
        self.master.config(menu=menu)

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

        self.button2 = tkinter.Button(self.canvas1, width=20, height=1, text='QML Details', state=tkinter.DISABLED,
                                      command=self.run_qml_details_dialogue)
        self.button2.grid(row=2, column=2, sticky='N')

        self.__button_dict['qml_details'] = self.button2
        self.button3 = tkinter.Button(self.canvas1, width=20, height=1, text='Find Variable', state=tkinter.DISABLED,
                                      command=self.run_find_variable_dialogue)
        self.button3.grid(row=3, column=2, sticky='N')
        self.__button_dict['find_variable'] = self.button3

        self.button4 = tkinter.Button(self.canvas1, width=20, height=1, text='Page Details', state=tkinter.DISABLED,
                                      command=self.run_show_page_details_dialogue)
        self.button4.grid(row=4, column=2, sticky='N')
        self.__button_dict['page_details'] = self.button4

        self.button5 = tkinter.Button(self.canvas1, width=20, height=1, text='Flowchart', state=tkinter.DISABLED,
                                      command=self.run_flowchart_dialog)
        self.button5.grid(row=5, column=2, sticky='N')
        self.__button_dict['flowchart'] = self.button5

        self.button6 = tkinter.Button(self.canvas1, width=20, height=1, text='', state=tkinter.DISABLED)
        self.button6.grid(row=6, column=2, sticky='N')
        self.__button_dict['btn6'] = self.button6

        self.button7 = tkinter.Button(self.canvas1, width=20, height=1, text='Open Path', state=tkinter.DISABLED,
                                      command=self.open_path)
        self.button7.grid(row=7, column=2, sticky='N')
        self.__button_dict['open_path'] = self.button7

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
        if len(self.listOfFiles) is 0:
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

    def load_files(self):
        self.logger.info('starting file dialog askopenfilenames')
        temp_files = list(filedialog.askopenfilenames(filetypes=(("xml files", "*.xml"), ("all files", "*.*"))))
        self.logger.info('opening files: ' + str(temp_files))
        if len(temp_files) is 0:
            return
        try:
            assert isinstance(temp_files, list)
        except AssertionError:
            self.logger.exception(
                'Assertion error: ' + str(temp_files) + ' \nis not a list, but of type: ' + str(type(temp_files)))
        temp_files = self.sort_list_of_files(temp_files)
        self.listOfFilesFull = temp_files
        self.listOfFiles = [os.path.split(f)[1] for f in temp_files]
        if len(temp_files) is 0:
            self.dirText = '(no path selected)'
        else:
            self.dirText = os.path.split(temp_files[0])[0]
        print(self.listOfFiles)
        self.redraw_path_label()
        self.redraw_file_text()

    def load_dir(self, extension='.xml'):
        self.logger.info('starting file dialog askdirectory')
        selected_path = filedialog.askdirectory()
        self.logger.info('selected path: ' + str(selected_path))
        if len(selected_path) is 0:
            return
        self.dirText = selected_path
        only_files = [f for f in listdir(selected_path) if
                      os.path.isfile(os.path.join(selected_path, f)) and os.path.splitext(f)[1] == '.xml']
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
        self.dict_of_qmls = {}
        if self.listOfFilesFull is []:
            return
        for entry in self.listOfFilesFull:
            print(entry)
            self.dict_of_qmls[os.path.split(entry)[1]] = QmlReader.QmlReader(entry)
        # self.read_into_questionnaire_objects()
        self.activate_button(['qml_details', 'flowchart', 'open_path'])

    # def read_into_questionnaire_objects(self):
    #   self.dict_of_questionnaires = {}
    #   for key in self.dict_of_qmls:
    #       self.dict_of_questionnaires[key] = Questionnaire.Questionnaire()
    #
    #            for page in self.dict_of_qmls[key].list_of_pages():
    #                self.read_into_questionnaire_objects(key=key, page=page)


    def read_into_page_objects(self, key_page, page):
                string_pagename = key_page
                dict_of_transitions = self.dict_of_qmls[key_page].dict_of_transitions[page]
                dict_of_sources = self.dict_of_qmls[key_page].dict_of_sources[page]
                list_of_variables = None
                question_string = None
                instruction_string = None
                title_string = None
                temp_page = Questionnaire.QmlPage(string_pagename=string_pagename,
                                                  dict_of_transitions=dict_of_transitions,
                                                  dict_of_sources=dict_of_sources,
                                                  list_of_variables=list_of_variables,
                                                  question_string=question_string,
                                                  instruction_string=instruction_string,
                                                  title_string=title_string)
                self.dict_of_questionnaires[key_page].add_page(temp_page)

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

        if action is 'details':
            self.window_selection.button1 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='Show details', state=tkinter.NORMAL,
                                                           command=self.details_show)

        if action is 'flowchart':
            self.window_selection.button1 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                           text='Flowchart(s)', state=tkinter.NORMAL,
                                                           command=self.flowchart_create)

        self.window_selection.button2 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                       text='Close', state=tkinter.NORMAL,
                                                       command=self.window_selection.destroy)
        self.window_selection.button1.grid(row=0, column=2, padx=0, sticky='NE')
        self.window_selection.button2.grid(row=1, column=2, padx=0, sticky='NE')

    def flowchart_create(self):
        self.logger.info('list of filenames from selection: ' + str(self.list_of_filenames_from_selection()))
        temp_list = [os.path.split(path)[1] for path in self.list_of_selected_files]
        [self.prepare_flowcharts(key) for key in temp_list]
        count = len(self.list_of_selected_files)
        if count is 1:
            tkinter.messagebox.showinfo('Succes', str(count) + ' flowchart has been created.')
        if count > 1:
            tkinter.messagebox.showinfo('Succes', str(count) + ' flowcharts have been created.')
        self.window_selection.destroy()

    def prepare_flowcharts(self, key):
        self.dict_of_qmls[key].transitions_to_nodes_edges(truncate=False)
        self.dict_of_qmls[key].init_pgv_graph()
        print(key)
        output_folder = str(os.path.join(str(self.dict_of_qmls[key].sourcepath), 'flowcharts'))
        try:
            mkdir(output_folder)
        except OSError as exc:
            self.logger.info('folder could not be created at first attempt: ' + output_folder)
            if exc.errno == errno.EEXIST and os.path.isdir(output_folder):
                self.logger.info('folder exists already: ' + output_folder)
                pass
            self.logger.exception('folder could not be created')

        t = time.localtime()
        timestamp = time.strftime('%Y-%m-%d_%H-%M', t)
        filename = timestamp + '_' + self.dict_of_qmls[key].sourcefilename
        self.logger.info('output_gml: ' + str(os.path.join(output_folder, filename + '.gml')))
        nx.write_gml(self.dict_of_qmls[key].DiGraph, os.path.join(output_folder, filename + '.gml'))
        self.logger.info('output_png: ' + str(os.path.join(output_folder, filename + '.gml')))
        self.dict_of_qmls[key].draw_pgv_graph(os.path.join(output_folder, filename + '.png'))

    def list_of_filenames_from_selection(self):
        local_list = [self.window_selection.dict_of_vars[i][0] for i in self.window_selection.dict_of_vars if
                      self.window_selection.dict_of_vars[i][1].get() is 1]
        self.logger.info('List of filenames from checkboxes created: ' + str(local_list))
        print('List of filenames from checkboxes created: ' + str(local_list))
        self.list_of_selected_files = local_list
        self.window_selection.details_string = self.details_preparation(local_list)

    def details_show(self):
        self.list_of_filenames_from_selection()

        for checkbox in self.window_selection.checkbox_list:
            checkbox.destroy()
        self.window_selection.button1.config(state=tkinter.DISABLED)
        self.window_selection.button3 = tkinter.Button(self.window_selection.canvas2, width=10, height=1,
                                                       text='Save as...', state=tkinter.NORMAL,
                                                       command=self.details_write_file)
        self.window_selection.button3.grid(row=0, column=2, padx=0, pady=0, sticky='NE')

        self.window_selection.text1 = scrolledtext.ScrolledText(self.window_selection, width=80, height=25)
        self.window_selection.text1.grid(row=0, column=0, sticky='W')
        self.window_selection.text1.insert(tkinter.END, self.window_selection.details_string)
        self.window_selection.text1.config(state=tkinter.NORMAL)

    def details_preparation(self, list_of_fullpaths):
        list_of_filenames = [os.path.split(file)[1] for file in list_of_fullpaths]
        return '\n\n###########################################\n\n'.join(
            ['filename: ' + str(key) + '\n\n' + self.details_prepare_from_qml(self.dict_of_qmls[key], self.logger) for
             key in self.dict_of_qmls if
             key in list_of_filenames])

    def details_write_file(self):
        self.logger.info('"save as" dialog starts')
        fullpath = tkinter.filedialog.asksaveasfilename(defaultextension='.txt', confirmoverwrite=True)
        self.logger.info('chosen full path: ' + str(fullpath))
        with open(fullpath, 'w') as file:
            file.writelines(self.window_selection.details_string)

    @staticmethod
    def details_prepare_from_qml(qml_reader_object, logger):
        """
        input: a single qml_reader_object
        :return: a string of details
        """
        try:
            assert isinstance(qml_reader_object, QmlReader.QmlReader)
        except AssertionError:
            logger.exception('Wrong input type: ' + str(type(qml_reader_object)))

        details_string = ''
        details_string += '\ntitle:\n'
        details_string += str(qml_reader_object.title)
        details_string += '\nlist of pages: [' + str(len(qml_reader_object.list_of_pages())) + ']\n'
        details_string += str(qml_reader_object.list_of_pages())
        details_string += '\n\n'
        details_string += '\nvariables extracted from pages: [' + str(
            len(qml_reader_object.list_of_variables_from_pages())) + ']\n'
        details_string += str(qml_reader_object.list_of_variables_from_pages())
        details_string += '\n\n'
        details_string += '\nvariables extracted from declaration: [' + str(
            len(qml_reader_object.list_of_variables_from_declaration())) + ']\n'
        details_string += str(qml_reader_object.list_of_variables_from_declaration())
        details_string += '\n\n'
        details_string += '\nunused variables:  [' + str(len(qml_reader_object.list_of_unused_variables())) + ']\n'
        details_string += str(qml_reader_object.list_of_unused_variables())
        details_string += '\n\n'
        details_string += '\npages declared in qml:  ['+ str(len(set(qml_reader_object.list_of_pages_declared))) + ']\n'
        details_string += str(set(qml_reader_object.list_of_pages_declared))
        details_string += '\n\n'
        details_string += '\npages not declared in qml, but mentioned in transitions:  [' + str(len(set(qml_reader_object.list_of_pages_not_declared_but_in_transitions))) + ']\n'
        details_string += str(set(qml_reader_object.list_of_pages_not_declared_but_in_transitions))

        return details_string

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


