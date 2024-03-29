__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.3.5"
__status__ = "Prototype"
__name__ = "Questionnaire"

# last edited: 2020-07-03

import re
import networkx as nx
import logging
import time
from os import path, mkdir
import errno
## noinspection PyUnresolvedReferences
import pygraphviz
from lxml import objectify


class Title:
    def __init__(self):
        pass


class UniqueObject(object):
    def __init__(self, uid):
        self.uid = None
        self.change_uid(uid)

    def change_uid(self, uid):
        assert isinstance(uid, str)
        self.uid = uid


class HeaderObject(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)
        self.set_uid(uid)

        self.text = None
        self.index = None
        self.tag = None
        self.allowed_tags_list = None
        self.visible_conditions = None

    def set_tag(self, tag_str):
        assert isinstance(tag_str, str)
        if tag_str in self.allowed_tags_list:
            self.tag = tag_str
        else:
            raise KeyError(
                'tag "' + str(tag_str) + '" not found in self.allowed_tags_list: ' + str(self.allowed_tags_list))

    def set_uid(self, uid):
        assert isinstance(uid, str)
        self.uid = uid

    def set_text(self, text):
        assert isinstance(text, str) or text is None
        self.text = text

    def set_visible_conditions(self, visible_conditions):
        assert isinstance(visible_conditions, str) or visible_conditions is None
        self.visible_conditions = visible_conditions

    def set_index(self, index):
        assert isinstance(index, int)
        self.index = index

    def __str__(self):
        return str(type(self).__name__) + '\n tag: ' + str(self.tag) + '\n index: ' + str(
            self.index) + '\n uid: ' + str(self.uid) + '\n visible: ' + str(
            self.visible_conditions) + '\n text: "' + str(self.text) + '"'


class PageHeaderObject(HeaderObject):
    def __init__(self, uid, text, tag, index, visible_conditions=None):
        super().__init__(uid)

        self.allowed_tags_list = ['instruction', 'introduction', 'text', 'title']
        self.set_tag(tag)

        self.set_text(text)
        self.set_index(index)
        self.set_visible_conditions(visible_conditions)


class QuestionHeaderObject(HeaderObject):
    def __init__(self, uid, text, tag, index, visible_conditions=None):
        super().__init__(uid)

        self.allowed_tags_list = ['instruction', 'introduction', 'question', 'text', 'title']
        self.set_tag(tag)

        self.set_text(text)
        self.set_index(index)
        self.set_visible_conditions(visible_conditions)


class Header:
    def __init__(self, reference_object_for_assertion):
        self.dict_of_header_objects = {}
        self.reference_object_for_assertion = reference_object_for_assertion

    def __str__(self):
        temp_str = 'header: ' + '\n'
        for key in self.dict_of_header_objects.keys():
            temp_str += 'uid: ' + self.dict_of_header_objects[key].uid + ', type: ' + str(
                self.dict_of_header_objects[key].print_type()) + ', text: "' + str(
                self.dict_of_header_objects[key].text) + '", visible conditions: "' + str(
                self.dict_of_header_objects[key].visible_conditions)[:10] + '"\n'
        return temp_str

    def add_header_object(self, page_header_object):
        '''
        :param reference_object_for_assertion:
        :param page_header_object:
        :return: None
        '''
        assert isinstance(page_header_object, self.reference_object_for_assertion)
        self.dict_of_header_objects[page_header_object.uid] = page_header_object

    def drop_header_object(self, uid):
        assert isinstance(uid, str)
        if uid in self.dict_of_header_objects:
            self.dict_of_header_objects.pop(uid)
        else:
            raise KeyError('UID ' + str(uid) + 'not found!')


class PageHeader(Header):
    def __init__(self):
        super().__init__(PageHeaderObject)


class QuestionHeader(Header):
    def __init__(self):
        super().__init__(QuestionHeaderObject)


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


class BodyQuestionTypes:
    def __init__(self):
        self.list_of_available_question_types = [BodyCalendar, BodyComparison, BodyMatrixDouble,
                                                 BodyMatrixMultipleChoice, BodyMatrixQuestionMixed,
                                                 BodyMatrixQuestionSingleChoice, BodyQuestionOpen]
        self.dict_of_question_tags = {}
        self.dict_of_question_types = {}
        for body_question_type_class in QuestionObject.__subclasses__():
            self.dict_of_question_types[getattr(body_question_type_class, '__name__')] = body_question_type_class
            # self.dict_of_question_tags[body_question_type_class.tag] = body_question_type_class

    def __str__(self):
        return str(self.dict_of_question_types.keys())


class Questions:
    def __init__(self):
        self.dict_of_question_objects = {}

    def add_question_object(self, question_object):
        assert isinstance(question_object, tuple(QuestionObject.__subclasses__()))
        assert question_object.uid not in self.dict_of_question_objects.keys()
        self.dict_of_question_objects[question_object.uid] = question_object

    def __str__(self):
        print('Question Objects')
        print(self.dict_of_question_objects)


class QuestionObject(UniqueObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid)
        self.variables = Variables()
        self.header = QuestionHeader()
        self.index = None
        self.tag = None
        self.set_tag(tag)
        self.set_index(index)

    def set_index(self, index):
        assert isinstance(index, int)
        self.index = index

    def set_tag(self, tag):
        assert (isinstance(tag, str))
        if tag != '':
            self.tag = tag


class BodyQuestionCalendar(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyCalendar(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyComparison(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class Display(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyMatrixDouble(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyMatrixMultipleChoice(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        self.uid = uid
        self.items = {}
        self.visible_condition = None
        pass

    def add_item(self, item):
        # self.item.uid = ""
        pass

    def list_vars(self):
        pass


class BodyMatrixQuestionMixed(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyMatrixQuestionOpen(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyMatrixQuestionSingleChoice(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyMultipleChoice(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyQuestionOpen(QuestionObject):
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


class BodyQuestionPretest(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodyQuestionSingleChoice(QuestionObject):
    def __init__(self, uid, index, tag):
        super().__init__(uid, index, tag)
        pass


class BodySection(UniqueObject):
    def __init__(self, uid):
        super().__init__(uid)


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
    def __init__(self, index, target, condition, source, distance):
        assert isinstance(index, int)
        assert isinstance(target, str)
        assert isinstance(source, str)
        assert isinstance(distance, int)
        assert isinstance(condition, str) or condition is None

        self.index = index
        self.target = target
        self.source = source
        self.distance = distance
        self.condition = condition
        self.condition_python = None
        self.condition_new = None

    def __str__(self):
        return f'{self.source}\t{self.target}\t{self.distance}\t{self.index}'


class TransitionLabels:
    def __init__(self):
        self.targets = []
        self.conditions = {}

    def add_targets_and_conditions(self, target, index, condition):
        assert isinstance(target, str) and isinstance(index, int) and isinstance(condition, str)
        if target not in self.targets:
            self.targets.append(target)
            self.conditions[target] = {index: condition}
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
        self.sources = {}

    def add_source(self, transition_object: Transition):
        assert isinstance(transition_object, Transition)

        if transition_object.source not in self.sources:
            self.sources[transition_object.source] = [transition_object]
        else:
            self.sources[transition_object.source].append(transition_object)


class Variable:
    def __init__(self, varname, vartype, varplace=None):
        self.__allowed_vartypes = ['boolean', 'singleChoiceAnswerOption', 'string', 'number']
        self.__allowed_varplaces = ['body', 'triggers', 'shown', None]
        if isinstance(varname, str) and isinstance(vartype, str):
            self.varname = varname
            if vartype in self.__allowed_vartypes:
                self.vartype = vartype
            else:
                raise ValueError('Vartype unknown/not allowed: ' + str(varname) + ', ' + str(vartype))
        else:
            raise TypeError('Input not of type string')

        self.set_varplace(varplace=varplace, varname=varname)

    def set_varplace(self, varplace, varname):
        if isinstance(varplace, str) or varplace is None:
            self.varplace = varplace
            if varplace in self.__allowed_varplaces:
                self.varplace = varplace
            else:
                raise ValueError('Varplace unknown/not allowed: ' + str(varname) + ', ' + str(varplace))
        else:
            raise TypeError('Input not of type string')
        return self

    def __str__(self):
        return str(self.varname)


class Variables:
    def __init__(self):
        self.variables = {}

    def __len__(self):
        return len(self.variables)

    def __str__(self):
        return str(self.list_details_str())

    def dict_details(self):
        """
        :return: dictionary of {varname: vartype}
        """
        dict_tmp = {}
        for var in self.variables:
            dict_tmp[var.varname] = self.variables[var].vartype
        return dict_tmp

    def list_all_shown_vars(self):
        return [var.varname for var in self.variables.values() if var.varplace == 'shown']

    def list_all_vars(self):
        return [var.varname for var in self.variables.values() if var.varplace != 'shown']

    def list_all_vars_types(self):
        return [(var.varname, var.vartype) for var in self.variables.values() if var.varplace != 'shown']

    def list_all_vartypes(self):
        return [var.vartype for var in self.variables.values()]

    def list_details_str(self):
        return [str(self.variables[var].varname) + ': ' + str(self.variables[var].vartype) for var in self.variables]

    def return_all_vars_as_dict(self):
        return self.variables

    def add_variable(self, variable_object, replace=False):
        if isinstance(variable_object, Variable):
            if variable_object.varname not in [self.variables[var].varname for var in self.variables]:
                self.variables[variable_object.varname] = variable_object
            else:
                if not replace:
                    # ToDo: error handling! maybe error message: yes/no ??
                    # raise ValueError('Variable name exists already!')
                    print("Variable " + str(variable_object.varname) + " already exists.")
        else:
            raise TypeError('Input not of type Variable')

    def delete_variable(self, varname):
        if isinstance(varname, str):
            tmp_list = [self.variables[var].varname for var in self.variables]
            tmp_var_list = self.variables.keys()
            if varname in tmp_list:
                for var in tmp_var_list:
                    if var.varname is varname:
                        self.variables.pop(var)
            else:
                raise ValueError('Varname not found!')
        else:
            raise TypeError('Input was not of type string!')

    def check_if_vartype(self, varname, vartype):
        if isinstance(varname, str) and isinstance(vartype, str):
            if varname in [self.variables[var].varname for var in self.variables]:
                for var in [self.variables[var] for var in self.variables if var.varname is varname]:
                    print(str(var))

                    return var.vartype is vartype
            else:
                raise ValueError('Varname not found!')
        else:
            raise TypeError('Input was not of type string!')


class QmlPages:
    def __init__(self):
        self.pages = {}

    def add_page(self, qmlpage, replace=False):
        assert isinstance(qmlpage, QmlPage)
        if qmlpage.uid in self.pages.keys():
            if not replace:
                raise KeyError('Page already exists and overwrite is False.')
            else:
                ('Page "' + qmlpage.uid + '" will be replaced.')
                self.pages[qmlpage.uid] = qmlpage
        else:
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

    def return_list_of_pagenames_with_condition_false(self) -> list:
        tmp_list = []
        for page_uid, page_object in self.pages.items():
            for source_uid, transition_list in page_object.sources.sources.items():
                for entry in transition_list:
                    if entry.condition == 'false':
                        if page_uid not in tmp_list:
                            tmp_list.append(page_uid)
        return tmp_list

    def return_list_of_pagenames_with_only_condition_false(self) -> list:
        tmp_list_of_pagenames_with_condition_false = self.return_list_of_pagenames_with_condition_false()
        tmp_list = []

        # iterate through all pages
        for page_uid, page_object in self.pages.items():
            # continue on next loop if page is not in list of pages with transition condition == false
            if page_uid not in tmp_list_of_pagenames_with_condition_false:
                continue

            # initiate a flag
            flag_non_false_transition = False

            # iterate through all sources Transition objects of this page
            for source_uid, transition_list in page_object.sources.sources.items():
                # iterate through all sources within list:
                for entry in transition_list:
                    # set flag = True if at least one condition is not 'false'
                    if entry.condition != 'false':
                        flag_non_false_transition = True
            if not flag_non_false_transition:
                tmp_list.append(page_uid)

        return tmp_list


class DuplicateVariables(Variables):
    def __init__(self):
        super().__init__()


class QmlPage(UniqueObject):
    def __init__(self, uid, declared=True):
        super().__init__(uid)
        self.declared = declared

        self.header = PageHeader()
        self.transitions = Transitions()
        self.variables = Variables()
        self.triggers = Triggers()
        self.sources = Sources()
        self.duplicate_variables = DuplicateVariables()
        self.questions = Questions()
        self.xml_source = None
        self.xml_source_str = None

    def set_xml_source(self, xml_source_code: objectify.ObjectifiedElement):
        self.xml_source = xml_source_code

    def set_xml_source_str(self, xml_source_code_str: str):
        self.xml_source_str = xml_source_code_str

    def add_sources(self, source):
        self.sources.add_source(source)

    def add_transition(self, transition):
        self.transitions.add_transitions(transition)

    def add_variable(self, variable):
        self.variables.add_variable(variable)

    def add_trigger(self, trigger):
        self.triggers.add_trigger(trigger)

    def add_header(self, header_text):
        self.header.add_header_object(header_text)

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
                if self.transitions.transitions[key]['condition'] is None:
                    self.transitions.transitions[key]['condition_python'] = 'True'
                else:
                    self.transitions.transitions[key]['condition_python'] = regex1.sub('is',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition'])
                    self.transitions.transitions[key]['condition_python'] = regex2.sub('is not',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex3.sub('>',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex4.sub('>=',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex5.sub('<',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex6.sub('<=',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex7.sub('int',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex8.sub('(\g<1> is None)',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex9.sub('is True',
                                                                                       self.transitions.transitions[
                                                                                           key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex10.sub('not ',
                                                                                        self.transitions.transitions[
                                                                                            key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex11.sub(' and ',
                                                                                        self.transitions.transitions[
                                                                                            key]['condition_python'])
                    self.transitions.transitions[key]['condition_python'] = regex12.sub(' or ',
                                                                                        self.transitions.transitions[
                                                                                            key]['condition_python'])


class Questionnaire:
    def __init__(self, file=None, filename='questionnaire', title='Zofar Survey'):
        """
        :param filename: string of source filename
        """
        self.__flowchart_show_conditions = True
        self.__flowchart_show_variable_names = True
        self.__flowchart_bidirectional_edges = False
        self.logger = logging.getLogger('debug')
        self.DiGraph = nx.DiGraph()
        self.filename = None
        self.file = file
        self.set_filename(filename)
        self.title = None
        self.set_title(title)
        self.pgv_graph = None
        self.variables = Variables()
        self.pages = QmlPages()

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

    def return_topologically_sorted_list_of_pages(self) -> list:
        self.transitions_to_nodes_edges_no_additional_node_label()
        list_of_looped_edges = []
        for u, v in self.DiGraph.edges:
            if u == v:
                list_of_looped_edges.append((u, v))

        for u, v in list_of_looped_edges:
            self.DiGraph.remove_edge(u, v)
        try:
            return [node for node in nx.topological_sort(self.DiGraph)]
        except nx.exception.NetworkXUnfeasible:
            return []

    def find_unused_variables(self):
        vars_from_pages_list = []
        for key, page in self.pages.pages.items():
            [vars_from_pages_list.append(i) for i in page.variables.list_all_vars()]

        # use set.symmetric_difference for better performance
        tmp_list = list(set(vars_from_pages_list).symmetric_difference(self.variables.list_all_vars()))
        tmp_list.sort()
        return tmp_list

    def return_list_of_all_transitions(self) -> list:
        list_of_all_transitions = []
        for pagename, page in self.pages.pages.items():
            if hasattr(page, 'transitions'):
                if hasattr(page.transitions, 'transitions'):
                    list_of_all_transitions += [transition for index, transition in
                                                page.transitions.transitions.items()]
        return list_of_all_transitions

    def return_list_of_transitions(self, min_distance: int = None, max_distance: int = 0, max_count: int = None,
                                   sort: bool = True,
                                   sort_key: str = 'distance') -> list:
        assert isinstance(min_distance, int) or min_distance is None
        assert isinstance(max_distance, int) or max_distance is None
        assert isinstance(max_count, int) or max_count is None
        assert isinstance(sort, bool)
        assert isinstance(sort_key, str) or sort_key is None

        if min_distance is None:
            min_distance = float('-inf')  # set value to negative infinity
        if max_distance is None:
            max_distance = float('inf')  # set value to positive infinity
        tmp_transitions_list = self.return_list_of_all_transitions()

        if sort:
            if sort_key is not None:
                # ToDo: assert / ensure that attribute is present in list elements
                tmp_transitions_list.sort(key=lambda distance: getattr(distance, sort_key))

        if max_count is None:
            max_count = len(tmp_transitions_list)

        return [transition for transition in tmp_transitions_list[:max_count] if
                min_distance < transition.distance < max_distance]

    def print_backwards_jumps(self, min_distance=None, max_distance=0, max_count=None):
        tmp_list = self.return_list_of_transitions(min_distance=min_distance, max_distance=max_distance,
                                                   max_count=max_count)
        return [str(entry) + '\n' for entry in tmp_list]

    def flowchart_set_show_variablenames(self, show_variablenames=True):
        """
        :param show_variablenames: True shows varnames, False omits them
        :return: none
        """
        assert isinstance(show_variablenames, bool)
        self.__flowchart_show_variable_names = show_variablenames

    def flowchart_set_show_conditions(self, show_conditions=True):
        """

        :param show_conditions: True shows conditions, False omits them
        :return: none
        """
        assert isinstance(show_conditions, bool)
        self.__flowchart_show_conditions = show_conditions

    def flowchart_set_bidirectional(self, set_biderectional=False):
        """

        :param set_biderectional: True duplicates all edges in opposing direction, False does nothing such.
        :return: none
        """
        assert isinstance(set_biderectional, bool)
        self.__flowchart_bidirectional_edges = set_biderectional

    def flowchart_create_birectional_edges(self):
        """
        duplicates the existing edges in opposing direction - only useful for weighted graphs/charts
        :return: none
        """
        for edge in self.DiGraph.edges():
            if edge[0] != edge[1]:
                self.DiGraph.add_edge(edge[1], edge[0])

    def transitions_to_nodes_edges_no_additional_node_label(self):
        for page in self.pages.pages.values():
            for transition in page.transitions.transitions.values():
                self.DiGraph.add_edge(page.uid, transition.target)

    def transitions_to_nodes_edges(self, truncate=False):
        self.DiGraph = nx.DiGraph()
        logging.info("transitions_to_nodes_edges")
        print("transitions_nodes_to_edges")
        self.create_readable_conditions()
        self.startup_logger(log_level=logging.DEBUG)

        for page in self.pages.pages.values():
            self.DiGraph.add_node(page.uid)  # create nodes

            cnt = 0
            dict_transitions = {}
            for transition in page.transitions.transitions.values():
                if transition.condition is not None:
                    if transition.target in dict_transitions.keys():
                        dict_transitions[transition.target] = dict_transitions[transition.target] + ' |\n(' + '[' + str(
                            cnt) + '] ' + transition.condition_new + ']' + ')'
                        if self.__flowchart_show_conditions:
                            self.DiGraph.add_edge(page.uid, transition.target,
                                                  label='[' + str(cnt) + '] ' + dict_transitions[transition.target])
                        else:
                            self.DiGraph.add_edge(page.uid, transition.target)
                    else:
                        dict_transitions[transition.target] = '(' + '[' + str(
                            cnt) + '] ' + transition.condition_new + ')'

                    if self.__flowchart_show_conditions:
                        self.DiGraph.add_edge(page.uid, transition.target, label=dict_transitions[transition.target])
                    else:
                        self.DiGraph.add_edge(page.uid, transition.target)

                else:  # if transition.condition is None
                    if transition.target in dict_transitions.keys():
                        if self.__flowchart_show_conditions:
                            self.DiGraph.add_edge(page.uid, transition.target, label='')
                        else:
                            self.DiGraph.add_edge(page.uid, transition.target)
                    else:
                        if cnt == 0:
                            if self.__flowchart_show_conditions:
                                self.DiGraph.add_edge(page.uid, transition.target, label='')
                            else:
                                self.DiGraph.add_edge(page.uid, transition.target)
                        if cnt != 0:
                            if self.__flowchart_show_conditions:
                                self.DiGraph.add_edge(page.uid, transition.target, label='[' + str(cnt) + ']')
                            else:
                                self.DiGraph.add_edge(page.uid, transition.target)
                cnt = cnt + 1

        if self.__flowchart_show_variable_names:
            self.add_variables_to_node()
        if self.__flowchart_bidirectional_edges:
            self.flowchart_create_birectional_edges()

    def add_variables_to_node(self):
        mapping = {}
        for pagename in self.pages.list_of_all_pagenames():
            tmp_output_string = ''
            tmp_var_list = self.pages.pages[pagename].variables.list_all_vars()
            if len(tmp_var_list) > 0:
                while len(tmp_var_list) > 3:
                    tmp_output_string += ', '.join(tmp_var_list[:3]) + ',\n'
                    tmp_var_list = tmp_var_list[3:]
                tmp_output_string += ', '.join(tmp_var_list) + ']'
                mapping[pagename] = pagename + '\n\n[' + tmp_output_string
        self.DiGraph = nx.relabel_nodes(self.DiGraph, mapping)

    def flowchart_create_graph(self, output_dir=None):
        """
        :param: None
        :return: None
        """
        logging.info("create_graph")
        self.transitions_to_nodes_edges()
        self.init_pgv_graph()
        self.prepare_and_draw_pgv_graph(output_dir=output_dir)

    def init_pgv_graph(self, graph_name='graph'):
        """
        :param: graph_name: string
        :return: None
        """
        logging.info("init_pgv_graph")
        self.pgv_graph = nx.nx_agraph.to_agraph(self.DiGraph)

        t = time.localtime()
        timestamp = time.strftime('%Y-%m-%d_%H-%M', t)

        self.pgv_graph.node_attr['shape'] = 'box'
        self.pgv_graph.graph_attr[
            'label'] = 'title: ' + self.title + '\nfile: ' + self.filename + '\n timestamp: ' + timestamp
        self.pgv_graph.layout(prog="dot")

    def prepare_and_draw_pgv_graph(self, output_dir=None):
        """
        prepares an output folder and timestampfs; draws the graph
        :param:
        :return:
        """
        logging.info("prepare_pgv_graph")

        if output_dir is None:
            output_folder = str(path.join(str(path.split(self.file)[0]), '../flowcharts'))
            self.logger.info('output_folder: ' + output_folder)
            try:
                mkdir(output_folder)
                self.logger.info('"' + output_folder + '" created.')
            except OSError as exc:
                self.logger.info('folder could not be created at first attempt: ' + output_folder)
                if exc.errno == errno.EEXIST and path.isdir(output_folder):
                    self.logger.info('folder exists already: ' + output_folder)
                    pass
                self.logger.exception('folder could not be created')
        else:
            output_folder = output_dir

        t = time.localtime()
        timestamp = time.strftime('%Y-%m-%d_%H-%M-%S', t)
        filename = timestamp + '_' + path.splitext(path.split(self.file)[1])[0]

        # gml output
        self.logger.info('output_gml: ' + str(path.join(output_folder, filename + '.gml')))
        nx.write_gml(self.DiGraph, path.join(output_folder, filename + '.gml'))

        # dot output

        self.logger.info('output_dot: ' + str(path.join(output_folder, filename + '.dot')))
        self.pgv_graph.write(path.join(output_folder, filename + '.dot'))

        # png output
        self.logger.info('output_png: ' + str(path.join(output_folder, filename + '.png')))
        self.draw_pgv_graph(path.join(output_folder, filename + '.png'))

    def draw_pgv_graph(self, output_file='output_file.png'):
        logging.info("draw_pgv_graph")
        self.pgv_graph.draw(output_file)

    def append_other_questionnaire(self, questionnaire_object):
        """
        :param: questionnaire_object: other Questionnaire.Questionnaire object that will be appended; duplicate pages in original Questionnaire will be overwritten by pages of the newly appended Questionnaire.
        :return: nothing.
        """
        self.logger.info(
            "processing questionnaire: " + str(questionnaire_object.file) + ' / ' + str(questionnaire_object.filename))
        assert isinstance(questionnaire_object, Questionnaire)

        for appended_page in questionnaire_object.pages.pages.values():
            self.logger.info("pages added: " + str(appended_page.uid))
            # ToDo: error handling! maybe error message: yes/no ?? output: list of duplicate pages / replaced pages
            self.pages.add_page(appended_page, replace=True)

        for appended_variable in questionnaire_object.variables.variables.values():
            # ToDo: error handling! maybe error message: yes/no ?? output: list of duplicate variables / replaced variables
            self.variables.add_variable(appended_variable)

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
                    transition.condition_new = regex12.sub(r'& \n', transition.condition_new)
                    transition.condition_new = regex13.sub(r'| \n', transition.condition_new)

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
