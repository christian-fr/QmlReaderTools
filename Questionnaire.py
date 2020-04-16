__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "Questionnaire"

# last edited: 2020-04-01

import re


class Calendar():
    def __init__(self):
        pass


class Comparison():
    def __init__(self):
        pass


class Display():
    def __init__(self):
        pass


class MatrixDouble():
    def __init__(self):
        pass


class MatrixMultipleChoice():
    def __init__(self, uid):
        self.uid = uid
        self.items = {}
        self.visible_condition = None
        pass

    def add_item(item):
        self.item.uid



    def list_vars(self):


class item():
    def __init__(self):
        self.uid = ""
        self.list_of_answeroptions = []
        pass

    def add_answeroption(self):


class answeroption():
    def __init__(self):
        self
        pass


class MatrixQuestionMixed():
    def __init__(self):
        pass


class MatrixQuestionOpen():
    def __init__(self):
        pass


class MatrixQuestionSingleChoice():
    def __init__(self):
        pass


class MultipleChoice():
    def __init__(self):
        pass


class QuestionOpen():
    def __init__(self, type='text'):
        self.type = type


class QuestionSingleChoice():
    def __init__(self):
        pass


class Unit():
    def __init__(self):
        pass


class Trigger():
    def __init__(self):
        pass


class Triggers():
    def __init__(self):
        pass


class Transition():
    def __init__(self, source, index, target, condition):
        self.source = source
        self.index = index
        self.target = target
        self.condition = condition
        self.condition_python =  None


class Transitions():
    def __init__(self):
        pass


class Variable():
    def __init__(self, varname, vartype):
        self.__allowed_vartypes = ['boolean', 'singleChoiceAnswerOption', 'text']
        if isinstance(varname, str) and isinstance(vartype, str):
            self.varname = varname
            if vartype in self.__allowed_vartypes:
                self.vartype = vartype
            else:
                raise ValueError('Vartype unknown/not allowd')
        else:
            raise TypeError('Input not of type string')

    def __str__(self):
        return str(self.varname)

class Variables():
    def __init__(self):
        self.list_of_variables = []

    def __len__(self):
        return len(self.list_of_variables)

    def __str__(self):
        return str(self.list_details_str())

    def dict_details(self):
        """
        :return: dictionary of {varname: vartype}
        """
        dict_tmp = {}
        for var in self.list_of_variables:
            dict_tmp[var.varname]=var.vartype
        return dict_tmp

    def list_all_vars(self):
        return [var.varname for var in self.list_of_variables]

    def list_all_vartypes(self):
        return [var.vartype for var in self.list_of_variables]

    def list_details_str(self):
        return [str(var.varname)+': '+str(var.vartype) for var in self.list_of_variables]

    def add_variable(self, variable_object):
        if isinstance(variable_object, Variable):
            if variable_object.varname not in [var.varname for var in self.list_of_variables]:
                self.list_of_variables.append(variable_object)
            else:
                raise ValueError('Variable name exists already!')
        else:
            raise TypeError('Input not of type Variable')

    def delete_variable(self, varname):
        if isinstance(varname, str):
            tmp_list = [var.varname for var in self.list_of_variables]
            tmp_var_list = self.list_of_variables
            if varname in tmp_list:
                for var in tmp_var_list:
                    if var.varname is varname:
                        self.list_of_variables.remove(var)
            else:
                raise ValueError('Varname not found!')
        else:
            raise TypeError('Input was not of type string!')

    def check_if_vartype(self, varname, vartype):
        if isinstance(varname, str) and isinstance(vartype, str):
            if varname in [var.varname for var in self.list_of_variables]:
                for var in [var for var in self.list_of_variables if var.varname is varname]:
                    print(str(var))

                    return var.vartype is vartype
            else:
                raise ValueError('Varname not found!')
        else:
            raise TypeError('Input was not of type string!')


class QmlPage:
    def __init__(self, string_pagename, dict_of_transitions=None, dict_of_sources=None, list_of_variables=None,
                 question_string=None,
                 instruction_string=None, title_string=None, declared=True):

        self.pagename = string_pagename

        self.declared = declared

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

# def file_saver_dialog():
#    root = tk.Tk()
#    save_path = filedialog.asksaveasfilename()
