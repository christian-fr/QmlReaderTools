__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "Questionnaire"

# last edited: 2020-04-01

import re


class Title:
    def __init__(self):
        pass


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

    def add_trigger(self, trigger):
        assert isinstance(trigger, Trigger)
        pass


class Transition:
    def __init__(self, index, target, condition):
        assert isinstance(index, int)
        assert isinstance(target, str)
        assert isinstance(condition, str) or condition is None

        self.index = index
        self.target = target
        self.condition = condition
        self.condition_python = None
        self.condition_new = None


class TransitionLabels:
    def __init__(self):
        self.targets = []
        self.conditions = {}

    def add_targets_and_conditions(self, target, index, condition):
        assert isinstance(target, str) and isinstance(index, int) and isinstance(condition, str)
        if target not in self.targets:
            self.targets.append(target)
            self.conditions[target] =  {index: condition}
        else:
            if index not in self.conditions[target]:
                self.conditions[target]['index'] = condition
            else:
                raise KeyError('Target "' + target + '" already in dictionary!')

class Transitions:
    def __init__(self):
        self.transitions = {}
        self.transition_labels = TransitionLabels()

    def add_transitions(self, transition):
        assert isinstance(transition, Transition)
        if transition.index not in self.transitions:
            self.transitions[transition.index] = transition
        else:
            raise ValueError('Index "' + '" already present in self.transitions!')


class Sources:
    def __init__(self):
        self.sources = []

    def add_source(self, source):
        assert isinstance(source, str)
        if source not in self.sources:
            self.sources.append(source)


class Variable:
    def __init__(self, varname, vartype):
        self.__allowed_vartypes = ['boolean', 'singleChoiceAnswerOption', 'string', 'number']
        if isinstance(varname, str) and isinstance(vartype, str):
            self.varname = varname
            if vartype in self.__allowed_vartypes:
                self.vartype = vartype
            else:
                raise ValueError('Vartype unknown/not allowed: ' + str(varname) + ', ' + str(vartype))
        else:
            raise TypeError('Input not of type string')

    def __str__(self):
        return str(self.varname)


class Variables:
    def __init__(self):
        self.dict_of_variables = {}

    def __len__(self):
        return len(self.dict_of_variables)

    def __str__(self):
        return str(self.list_details_str())

    def dict_details(self):
        """
        :return: dictionary of {varname: vartype}
        """
        dict_tmp = {}
        for var in self.dict_of_variables:
            dict_tmp[var.varname] = self.dict_of_variables[var].vartype
        return dict_tmp

    def list_all_vars(self):
        return [var.varname for var in self.dict_of_variables]

    def list_all_vartypes(self):
        return [var.vartype for var in self.dict_of_variables]

    def list_details_str(self):
        return [str(self.dict_of_variables[var].varname) + ': ' + str(self.dict_of_variables[var].vartype) for var in self.dict_of_variables]

    def add_variable(self, variable_object):
        if isinstance(variable_object, Variable):
            if variable_object.varname not in [self.dict_of_variables[var].varname for var in self.dict_of_variables]:
                self.dict_of_variables[variable_object.varname] = variable_object
            else:
                raise ValueError('Variable name exists already!')
        else:
            raise TypeError('Input not of type Variable')

    def delete_variable(self, varname):
        if isinstance(varname, str):
            tmp_list = [self.dict_of_variables[var].varname for var in self.dict_of_variables]
            tmp_var_list = self.dict_of_variables.keys()
            if varname in tmp_list:
                for var in tmp_var_list:
                    if var.varname is varname:
                        self.dict_of_variables.pop(var)
            else:
                raise ValueError('Varname not found!')
        else:
            raise TypeError('Input was not of type string!')

    def check_if_vartype(self, varname, vartype):
        if isinstance(varname, str) and isinstance(vartype, str):
            if varname in [self.dict_of_variables[var].varname for var in self.dict_of_variables]:
                for var in [self.dict_of_variables[var] for var in self.dict_of_variables if var.varname is varname]:
                    print(str(var))

                    return var.vartype is vartype
            else:
                raise ValueError('Varname not found!')
        else:
            raise TypeError('Input was not of type string!')


class QmlPages:
    def __init__(self):
        self.pages = {}

    def add_page(self, qmlpage):
        assert isinstance(qmlpage, QmlPage)
        self.pages[qmlpage.uid] = qmlpage

    def drop_page(self, uid):
        assert isinstance(uid, str)
        if uid in self.pages:
            self.pages.pop(uid)
        else:
            raise ValueError('Pagename "' + str(uid) + '" not found in self.pages!')

    def list_of_all_pagenames(self):
        tmp_list = []
        for key in self.pages:
            tmp_list.append(key)
        return tmp_list

class QmlPage(UniqueObject):
    def __init__(self, uid, declared=True):
        super().__init__(uid)
        self.declared = declared

        self.header = Header()
        self.transitions = Transitions()
        self.variables = Variables()
        self.triggers = Triggers()
        self.sources = Sources()

    def add_sources(self, source):
        self.sources.add_source(source)

    def add_transition(self, transition):
        self.transitions.add_transitions(transition)

    def add_variable(self, variable):
        self.variables.add_variable(variable)

    def add_trigger(self, trigger):
        self.triggers.add_trigger(trigger)

    def add_header(self, header_text):
        self.header.add_header_text(header_text)

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


class Questionnaire:
    def __init__(self, filename='questionnaire', title='Zofar Survey'):
        """
        :param filename: string of source filename
        """
        self.filename = None
        self.set_filename(filename)
        self.title = None
        self.set_title(title)

        self.variables = Variables()
        self.pages = QmlPages()

    def create_readable_conditions(self):
        regex1 = re.compile(r'\s+')
        regex2 = re.compile(r'zofar\.asNumber\(([a-z0-9A-Z_\-]+)\)')
        regex3 = re.compile(r'==([0-9])')
        regex4a = re.compile(r'!zofar\.isMissing\(([a-z0-9A-Z\-_]+)\)')
        regex4b = re.compile(r'zofar\.isMissing\(([a-z0-9A-Z\-_]+)\)')
        regex5 = re.compile(r'!([a-z0-9A-Z\-_]+)\.value')
        regex6 = re.compile(r'([a-z0-9A-Z\-_]+)\.value')
        regex7 = re.compile(r' and ')
        regex8 = re.compile(r' or ')
        regex9 = re.compile(r'PRELOAD')
        regex10 = re.compile(r'dropDown')
        regex11 = re.compile(r'replace.*[^ ]$')
        regex12 = re.compile(r'\&')
        regex13 = re.compile(r'\|')

        for page in self.pages.pages.values():
            for transition in page.transitions.transitions.values():
                if transition.condition is not None:
                    transition.condition_new = regex1.sub(' ', transition.condition)
                    transition.condition_new = regex2.sub(r'\g<1> ', transition.condition_new)
                    transition.condition_new = regex3.sub(r'== \g<1>', transition.condition_new)
                    transition.condition_new = regex4a.sub(r'\g<1> != MISS', transition.condition_new)
                    transition.condition_new = regex4b.sub(r'\g<1> == MISS', transition.condition_new)
                    transition.condition_new = regex5.sub(r'\g<1> != 1', transition.condition_new)
                    transition.condition_new = regex6.sub(r'\g<1> == 1', transition.condition_new)
                    transition.condition_new = regex7.sub(r' & ', transition.condition_new)
                    transition.condition_new = regex8.sub(r' | ', transition.condition_new)
                    transition.condition_new = regex9.sub(r'', transition.condition_new)
                    transition.condition_new = regex10.sub(r'', transition.condition_new)
                    transition.condition_new = regex12.sub(r'& \n',transition.condition_new)
                    transition.condition_new = regex13.sub(r'| \n',transition.condition_new)

    def set_title(self, title):
        assert isinstance(title, str)
        self.title = title

    def drop_page(self, uid):
        pass

    def create_dict_of_variables(self):
        raise NotImplementedError

    def set_filename(self, filename):
        assert isinstance(filename, str)
        self.filename = filename



