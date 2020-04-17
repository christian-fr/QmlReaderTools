__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "Questionnaire"

# last edited: 2020-04-01

import re


class UniqueObject:
    def __init__(self, uid):
        self.uid = None
        self.change_uid(uid)

    def change_uid(self, uid):
        assert isinstance(uid, str)
        self.uid = uid


class Calendar(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class Comparison(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class Display(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class MatrixDouble(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class MatrixMultipleChoice(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        self.uid = uid
        self.items = {}
        self.visible_condition = None
        pass

    def add_item(self, item):
        # self.item.uid = ""
        pass

    def list_vars(self):
        pass


class HeaderText(UniqueObject):
    def __init__(self, uid, text, visible_conditions=None):
        super().__init__(uid)
        self.change_uid(uid)
        self.text = None
        self.change_text(text)
        self.visible_conditions = None
        self.change_visible_conditions(visible_conditions)

    def change_uid(self, uid):
        assert isinstance(uid, str)
        self.uid = uid

    def change_text(self, text):
        assert isinstance(text, str)
        self.text = text

    def change_visible_conditions(self, visible_conditions):
        assert isinstance(visible_conditions, str) or visible_conditions is None
        self.visible_conditions = visible_conditions


class Question(HeaderText):
    def __init__(self, uid, text):
        super().__init__(uid, text)

    @staticmethod
    def print_type():
        return 'question'


class Instruction(HeaderText):
    def __init__(self, uid, text):
        super().__init__(uid, text)

    @staticmethod
    def print_type():
        return 'instruction'


class Introduction(HeaderText):
    def __init__(self, uid, text):
        super().__init__(uid, text)

    @staticmethod
    def print_type():
        return 'introduction'


class Header:
    def __init__(self):
        self.dict_of_header_texts = {}

    def __str__(self):
        temp_str = 'header: ' + '\n'
        for key in self.dict_of_header_texts.keys():
            temp_str += 'uid: ' + self.dict_of_header_texts[key].uid + ', type: ' + str(
                self.dict_of_header_texts[key].print_type()) + ', text: "' + str(
                self.dict_of_header_texts[key].text) + '", visible conditions: "' + str(
                self.dict_of_header_texts[key].visible_conditions)[:10] + '"\n'
        return temp_str

    def add_header_text(self, header_text):
        assert isinstance(header_text, Question) or isinstance(header_text, Introduction) or isinstance(header_text,
                                                                                                        Instruction)
        self.dict_of_header_texts[header_text.uid] = header_text

    def drop_header_text(self, uid):
        if uid in self.dict_of_header_texts:
            self.dict_of_header_texts.pop(uid)
        pass


class ResponseDomain(UniqueObject):
    def __init__(self, uid, variable, visible_condition):
        super().__init__(uid)
        self.variable = None
        self.change_variable(variable)
        self.visible_condition = None
        self.change_visible_conditions(visible_condition)
        self.dict_of_items = {}
        self.dict_of_answeroptions = {}

    def add_item(self, item):
        assert isinstance(item, Item)
        if self.dict_of_answeroptions != {}:
            raise KeyError('Answeroptions already present while trying to add an Item - both are not allowed next to '
                           'each other at this level!')
        if item.uid not in self.dict_of_items:
            self.dict_of_items[item.uid] = item
        else:
            raise KeyError('duplicate uid of item: "' + str(item.uid) + '" already present!')

    def add_answeroption(self, answeroption):
        assert isinstance(answeroption, AnswerOption)
        if self.dict_of_items != {}:
            raise KeyError('Items already present while trying to add an AnswerOption - both are not allowed next to '
                           'each other at this level!')
        if answeroption.uid not in self.dict_of_answeroptions:
            self.dict_of_answeroptions[answeroption.uid] = answeroption
        else:
            raise KeyError('duplicate uid of item: "' + str(answeroption.uid) + '" already present!')

    def drop_answeroption(self, uid):
        if uid in self.dict_of_answeroptions:
            self.dict_of_answeroptions.pop(uid)
        pass

    def drop_item(self, uid):
        if uid in self.dict_of_items:
            self.dict_of_items.pop(uid)
        pass

    def change_variable(self, variable):
        assert isinstance(variable, str)
        self.variable = variable

    def change_visible_conditions(self, visible_conditions):
        assert isinstance(visible_conditions, str)
        self.visible_condition = visible_conditions


class Item(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        self.dict_of_answeroptions = {}
        pass

    def __str__(self):
        temp_str = 'item uid: ' + str(self.uid) + '\n'
        for key in self.dict_of_answeroptions.keys():
            temp_str += 'uid: ' + self.dict_of_answeroptions[key].uid + ', label: ' + str(
                self.dict_of_answeroptions[key].labeltext) + ', value: ' + str(
                self.dict_of_answeroptions[key].value) + ', missing: ' + str(
                self.dict_of_answeroptions[key].missing) + '\n'
        return temp_str

    def add_answeroption(self, answeroption):
        assert isinstance(answeroption, AnswerOption)
        if answeroption.uid not in self.dict_of_answeroptions:
            self.dict_of_answeroptions[answeroption.uid] = answeroption
        else:
            raise KeyError('duplicate uid of answeroptions: "' + str(answeroption.uid) + '" already present!')

    def drop_answeroption(self):
        pass


class AnswerOption(UniqueObject):
    def __init__(self, uid, value, labeltext=None, missing=False):
        super().__init__(uid)
        self.labeltext = None
        self.value = None
        self.missing = False
        self.change_labeltext(labeltext)
        self.change_value(value)
        self.set_missing(missing)
        pass

    def __str__(self):
        return 'label: "' + str(self.labeltext) + '", value: ' + str(self.value) + ', missing: ' + str(self.missing)

    def change_labeltext(self, labeltext):
        """
        :param labeltext: string or none
        :return: nothing
        """
        assert isinstance(labeltext, str) or labeltext is None
        self.labeltext = labeltext

    def change_value(self, value):
        """
        :param value: string value
        :return: nothing
        """
        assert isinstance(value, str)
        self.value = value

    def set_missing(self, missing):
        """
        :param missing: boolean value
        :return:
        """
        assert missing is True or missing is False
        self.missing = missing


class MatrixQuestionMixed(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class MatrixQuestionOpen(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class MatrixQuestionSingleChoice(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        self.header = Header()
        pass


class MultipleChoice(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class QuestionOpen(UniqueObject):
    def __init__(self, uid, variable, text_type='text', prefix=None, postfix=None):
        super().__init__(uid)
        self.text_type = None
        self.__allowed_text_types = ['grade', 'number', 'text']
        self.type = None
        self.change_text_type(text_type)
        self.variable = None
        self.set_variable(variable)
        self.prefix = None
        self.postfix = None
        self.set_prefix(prefix)
        self.set_postfix(postfix)

    def set_prefix(self, prefix):
        assert isinstance(prefix, str)
        self.prefix = prefix

    def set_postfix(self, postfix):
        assert isinstance(postfix, str)
        self.postfix = postfix

    def set_variable(self, variable):
        assert isinstance(variable, Variable)
        self.variable = variable

    def change_text_type(self, text_type):
        assert isinstance(text_type, str)
        if text_type in self.__allowed_text_types:
            self.text_type = text_type
        else:
            raise ValueError('QuestionOpen: text type "' + str(text_type) + '" not allowed.')


class QuestionSingleChoice(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class Unit(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        pass


class Trigger:
    def __init__(self):
        pass


class Triggers:
    def __init__(self):
        pass


class Transition:
    def __init__(self, source, index, target, condition):
        self.source = source
        self.index = index
        self.target = target
        self.condition = condition
        self.condition_python = None


class Transitions:
    def __init__(self):
        pass


class Variable:
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


class Variables:
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
            dict_tmp[var.varname] = var.vartype
        return dict_tmp

    def list_all_vars(self):
        return [var.varname for var in self.list_of_variables]

    def list_all_vartypes(self):
        return [var.vartype for var in self.list_of_variables]

    def list_details_str(self):
        return [str(var.varname) + ': ' + str(var.vartype) for var in self.list_of_variables]

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
            for key in self.transitions.keys():
                if self.transitions[key]['condition'] is None:
                    self.transitions[key]['condition_python'] = 'True'
                else:
                    self.transitions[key]['condition_python'] = regex1.sub('is', self.transitions[key]['condition'])
                    self.transitions[key]['condition_python'] = regex2.sub('is not',
                                                                           self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex3.sub('>', self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex4.sub('>=', self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex5.sub('<', self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex6.sub('<=', self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex7.sub('int', self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex8.sub('(\g<1> is None)',
                                                                           self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex9.sub('is True',
                                                                           self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex10.sub('not ',
                                                                            self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex11.sub(' and ',
                                                                            self.transitions[key]['condition_python'])
                    self.transitions[key]['condition_python'] = regex12.sub(' or ',
                                                                            self.transitions[key]['condition_python'])

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
        """
        :param pages: dictionary of Questionnaire.QmlPage objects
        """

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


a = AnswerOption('ao1', '1')
b = AnswerOption('ao3', '3', labeltext="hey ho")
c = AnswerOption('ao4', '4', missing=True)

i = Item('it1')
i.add_answeroption(a)
i.add_answeroption(b)
i.add_answeroption(c)

print(i)

q = Question('a', 'how are you?')
i = Instruction('i1', 'Please do it this way.')
intro = Introduction('in1', 'This is a questionnaire.')

head = Header()
head.add_header_text(q)
head.add_header_text(i)
head.add_header_text(intro)
print(head)
