__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "Questionnaire"
# last edited: 2020/03/12

import re

class QmlPage:
    def __init__(self, string_pagename, dict_of_transitions=None, dict_of_sources=None, list_of_variables=None, question_string=None,
                 instruction_string=None, title_string=None):
        self.pagename = string_pagename

        if dict_of_transitions is None:
            dict_of_transitions = {}
        self.transitions = dict_of_transitions

        if dict_of_sources is None:
            dict_of_sources = {}
        self.sources = dict_of_sources


        if list_of_variables is None:
            list_of_variables = []
        self.variables = list_of_variables

        self.questions = question_string
        self.instructions = instruction_string
        self.title = title_string

    def add_transition(self, transition_dict):
        """
        :param transition_dict:
            {order(integer): {'target': string, 'condition': string -> has to be python evaluation}}
        :return:
        """

        if transition_dict is {}:
            pass
        elif isinstance(transition_dict, dict):
            for key in transition_dict.keys():
                if isinstance(key, int) and isinstance(transition_dict[key], dict) and (
                        transition_dict[key]['condition'] is None or isinstance(transition_dict[key]['condition'],
                                                                                str)):
                    pass
                else:
                    raise ValueError
        else:
            raise ValueError

        self.transitions = transition_dict
        self.__translate_transition_condition_to_python_syntax()

    def __translate_transition_condition_to_python_syntax(self):
        regex1 = re.compile(r'==')  # 'is'
        regex2 = re.compile(r'!=')  # 'is not'
        regex3 = re.compile(r'gt')  # '>'
        regex4 = re.compile(r'ge')  # '>='
        regex5 = re.compile(r'lt')  # '<'
        regex6 = re.compile(r'le')  # '<='
        regex7 = re.compile(r'zofar.asNumber')  # 'int'
        regex8 = re.compile(r'zofar.isMissing\(([a-zA-Z0-9\-_]+)\)')  # '(\1 is None)'
        regex9 = re.compile(r'.value')  # 'is True'
        regex10 = re.compile(r'!')  # 'not'
        regex11 = re.compile(r' AND ')  # ' and '
        regex12 = re.compile(r' OR ')  # ' or '

        if self.transitions is not {}:
            for i in self.transitions.keys():
                if self.transitions[i]['condition'] is None:
                    self.transitions[i]['condition_python'] = 'True'
                else:
                    self.transitions[i]['condition_python'] = regex1.sub('is', self.transitions[i]['condition'])
                    self.transitions[i]['condition_python'] = regex2.sub('is not',
                                                                         self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex3.sub('>', self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex4.sub('>=', self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex5.sub('<', self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex6.sub('<=', self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex7.sub('int', self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex8.sub('(\g<1> is None)',
                                                                         self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex9.sub('is True',
                                                                         self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex10.sub('not ',
                                                                          self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex11.sub(' and ',
                                                                          self.transitions[i]['condition_python'])
                    self.transitions[i]['condition_python'] = regex12.sub(' or ',
                                                                          self.transitions[i]['condition_python'])

    def add_variable(self, variable_dict):
        """
        :param variable_dict:
            {'variablename': string, 'levels': list of integers}
        :return:
        """
        if variable_dict is {}:
            return

    def add_question(self, question_string):
        raise NotImplementedError

    def add_instruction(self, instruction_string):
        raise NotImplementedError


class Questionnaire:
    def __init__(self, pages=None):
        '''
        :param pages: dictionary of Questionnaire.QmlPage objects
        '''

        if pages is None:
            pages = {}
        self.__pages = pages
        self.__variables_dict = {}

    def add_page(self, page):
        if isinstance(page, QmlPage):
            self.__pages[page.pagename] = page
        else:
            raise ValueError("Object added was not of type QmlPage")

    def create_dict_of_variables(self):
        raise NotImplementedError


#def file_saver_dialog():
#    root = tk.Tk()
#    save_path = filedialog.asksaveasfilename()


