__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.4.0"
__status__ = "Prototype"
__name__ = "QuestionnaireObject"




import re
import networkx as nx
import logging
import time
from os import path, mkdir
from sys import platform
import errno
# noinspection PyUnresolvedReferences
if not platform == 'win32':
    import pygraphviz
import QuestionnaireElements


class QuestionnaireObject:
    def __init__(self, file=None, title='Zofar Survey'):
        """
        :param file: string of source filename
        """
        self.__flowchart_show_conditions = True
        self.__flowchart_show_variable_names = True
        self.__flowchart_bidirectional_edges = False
        self.logger = logging.getLogger('debug')
        self.DiGraph = nx.DiGraph()
        self.file = file
        self.title = title
        self.pgv_graph = None
        # ToDo: implement as methods (add, get, get_all=
        # self.variables = QuestionnaireElements.
        self.pages_dict = {}
        self.used_variables_dict = {}
        self.declared_variables_dict = {}
        self.duplicate_variables_dict = {}

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title_string):
        assert isinstance(title_string, str)
        self.__title = title_string

    @property
    def file(self):
        return self.__filename

    @file.setter
    def file(self, filename_string):
        assert isinstance(filename_string, str)
        self.__filename = filename_string

    def get_page_from_uid(self, page_uid):
        assert isinstance(page_uid, str)
        if page_uid in self.pages_dict.keys():
            return self.pages_dict[page_uid]
        else:
            raise KeyError('Page with uid="{0}" not found in pages_dict of questionnaire with filename="{1}", title="{2}"'.format(page_uid, str(self.file), self.title))

    def get_all_pages_list(self):
        return list(self.pages_dict.keys())

    def add_page(self, page_object):
        assert isinstance(page_object, QuestionnaireElements.PageObject)
        if page_object.uid not in self.pages_dict.keys():
            self.pages_dict[page_object.uid] = page_object
        else:
            raise KeyError('Page with uid="{0}" already present in pages_dict in questionnaire title="{1}", filename="{2}"'.format(page_object.uid, self.title, str(self.file)))

    def add_variables_to_declared_variables_dict(self, variable_object):
        assert isinstance(variable_object, QuestionnaireElements.VariableObject)
        if variable_object.name not in self.used_variables_dict.keys():
            self.declared_variables_dict[variable_object.name] = variable_object
        else:
            raise KeyError('Variable with name="{0}" already present in declared_variables_dict in questionnaire with filename="{1}", title="{2}'.format(variable_object.name, str(self.file), self.title))

    def add_variables_to_used_variables_dict(self, variable_object):
        assert isinstance(variable_object, QuestionnaireElements.VariableObject)
        if variable_object.name not in self.used_variables_dict.keys():
            self.used_variables_dict[variable_object.name] = variable_object
        else:
            if variable_object.name not in self.duplicate_variables_dict.keys():
                self.duplicate_variables_dict[variable_object.name] = [self.used_variables_dict[variable_object.name], variable_object]
            else:
                self.duplicate_variables_dict[variable_object.name].append(variable_object)

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

    def flowchart_set_show_variable_names(self, show_variablenames=True):
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

    def flowchart_create_bidirectional_edges(self):
        """
        duplicates the existing edges in opposing direction - only useful for weighted graphs/charts
        :return: none
        """
        for edge in self.DiGraph.edges():
            if edge[0] != edge[1]:
                self.DiGraph.add_edge(edge[1], edge[0])

    def transitions_to_nodes_edges(self, truncate=False):
        self.DiGraph = nx.DiGraph()
        logging.info("transitions_to_nodes_edges")
        print("transitions_nodes_to_edges")
        self.create_readable_conditions()
        self.startup_logger(log_level=logging.DEBUG)

        for page in self.pages_dict.values():
            self.DiGraph.add_node(page.uid)  # create nodes

            cnt = 0
            dict_transitions = {}
            for transition in page.transitions_dict.transitions.values():
                if transition.condition is not None:
                    if transition.target in dict_transitions.keys():
                            dict_transitions[transition.target] = dict_transitions[transition.target] + ' |\n(' + '[' + str(cnt) + '] ' + transition.condition_new + ']' + ')'
                            if self.__flowchart_show_conditions:
                                self.DiGraph.add_edge(page.question_uid, transition.target, label='[' + str(cnt) + '] ' + dict_transitions[transition.target])
                            else:
                                self.DiGraph.add_edge(page.question_uid, transition.target)
                    else:
                        dict_transitions[transition.target] = '(' + '[' + str(cnt) + '] ' + transition.condition_new + ')'

                    if self.__flowchart_show_conditions:
                        self.DiGraph.add_edge(page.question_uid, transition.target, label=dict_transitions[transition.target])
                    else:
                        self.DiGraph.add_edge(page.question_uid, transition.target)

                else:  # if transition.condition is None
                    if transition.target in dict_transitions.keys():
                        if self.__flowchart_show_conditions:
                            self.DiGraph.add_edge(page.question_uid, transition.target, label='')
                        else:
                            self.DiGraph.add_edge(page.question_uid, transition.target)
                    else:
                        if cnt == 0:
                            if self.__flowchart_show_conditions:
                                self.DiGraph.add_edge(page.question_uid, transition.target, label='')
                            else:
                                self.DiGraph.add_edge(page.question_uid, transition.target)
                        if cnt != 0:
                            if self.__flowchart_show_conditions:
                                self.DiGraph.add_edge(page.question_uid, transition.target, label='[' + str(cnt) + ']')
                            else:
                                self.DiGraph.add_edge(page.question_uid, transition.target)
                cnt = cnt + 1

        if self.__flowchart_show_variable_names:
            self.add_variables_to_node()
        if self.__flowchart_bidirectional_edges:
            self.flowchart_create_bidirectional_edges()

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



    def flowchart_create_graph(self):
        """
        :param: None
        :return: None
        """
        logging.info("create_graph")
        self.transitions_to_nodes_edges()
        self.init_pgv_graph()
        self.prepare_and_draw_pgv_graph()


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
        self.pgv_graph.graph_attr['label'] = 'title: ' + self.title + '\nfile: ' + self.filename + '\n timestamp: ' + timestamp
        self.pgv_graph.layout("dot")

    def prepare_and_draw_pgv_graph(self):
        """
        prepares an output folder and timestampfs; draws the graph
        :param:
        :return:
        """
        logging.info("prepare_pgv_graph")
        output_folder = str(path.join(str(path.split(self.file)[0]), 'flowcharts'))
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

        t = time.localtime()
        timestamp = time.strftime('%Y-%m-%d_%H-%M', t)
        filename = timestamp + '_' + path.splitext(path.split(self.file)[1])[0]
        self.logger.info('output_gml: ' + str(path.join(output_folder, filename + '.gml')))
        nx.write_gml(self.DiGraph, path.join(output_folder, filename + '.gml'))
        self.logger.info('output_png: ' + str(path.join(output_folder, filename + '.png')))
        self.pgv_graph.write(path.join(output_folder, filename + '.dot'))
        self.logger.info('output_dot: ' + str(path.join(output_folder, filename + '.dot')))
        self.draw_pgv_graph(path.join(output_folder, filename + '.png'))

    def draw_pgv_graph(self, output_file='output_file.png'):
        logging.info("draw_pgv_graph")
        self.pgv_graph.draw(output_file)

    def append_other_questionnaire(self, questionnaire_object):
        """
        :param: questionnaire_object: other Questionnaire.Questionnaire object that will be appended; duplicate pages in original Questionnaire will be overwritten by pages of the newly appended Questionnaire.
        :return: nothing.
        """
        self.logger.info("processing questionnaire: " + str(questionnaire_object.file) + ' / ' + str(questionnaire_object.filename))
        assert isinstance(questionnaire_object, QuestionnaireObject)

        for appended_page in questionnaire_object.pages.pages.values():
            self.logger.info("pages added: " + str(appended_page.question_uid))
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

    def drop_page(self, uid):
        pass

    def create_dict_of_variables(self):
        raise NotImplementedError



#
# class Title:
#     def __init__(self):
#         pass
#
#
# class UniqueObject(object):
#     def __init__(self, uid):
#         self.uid = None
#         self.change_uid(uid)
#
#     def change_uid(self, uid):
#         assert isinstance(uid, str)
#         self.uid = uid
#
# class HeaderObject(UniqueObject):
#     def __init__(self, uid):
#         super().__init__(uid)
#         self.set_uid(uid)
#
#         self.text = None
#         self.index = None
#         self.tag = None
#         self.allowed_tags_list = None
#         self.visible_conditions = None
#
#     def set_tag(self, tag_str):
#         assert isinstance(tag_str, str)
#         if tag_str in self.allowed_tags_list:
#             self.tag = tag_str
#         else:
#             raise KeyError('tag "' + str(tag_str) + '" not found in self.allowed_tags_list: ' + str(self.allowed_tags_list))
#
#     def set_uid(self, uid):
#         assert isinstance(uid, str)
#         self.uid = uid
#
#     def set_text(self, text):
#         assert isinstance(text, str)
#         self.text = text
#
#     def set_visible_conditions(self, visible_conditions):
#         assert isinstance(visible_conditions, str) or visible_conditions is None
#         self.visible_conditions = visible_conditions
#
#     def set_index(self, index):
#         assert isinstance(index, int)
#         self.index = index
#
#     def __str__(self):
#         return str(type(self).__name__) + '\n tag: ' + str(self.tag) + '\n index: ' + str(self.index) + '\n uid: ' + str(self.uid) + '\n visible: ' + str(self.visible_conditions) + '\n text: "' + str(self.text) + '"'
#
#
# class PageHeaderObject(HeaderObject):
#     def __init__(self, uid, text, tag, index, visible_conditions=None):
#         super().__init__(uid)
#
#         self.allowed_tags_list = ['instruction', 'introduction', 'text', 'title']
#         self.set_tag(tag)
#
#         self.set_text(text)
#         self.set_index(index)
#         self.set_visible_conditions(visible_conditions)
#
#
# class QuestionHeaderObject(HeaderObject):
#     def __init__(self, uid, text, tag, index, visible_conditions=None):
#         super().__init__(uid)
#
#         self.allowed_tags_list = ['instruction', 'introduction', 'question', 'text', 'title']
#         self.set_tag(tag)
#
#         self.set_text(text)
#         self.set_index(index)
#         self.set_visible_conditions(visible_conditions)
#
# class Header:
#     def __init__(self, reference_object_for_assertion):
#         self.dict_of_header_objects = {}
#         self.reference_object_for_assertion = reference_object_for_assertion
#
#     def __str__(self):
#         temp_str = 'header: ' + '\n'
#         for key in self.dict_of_header_objects.keys():
#             temp_str += 'uid: ' + self.dict_of_header_objects[key].question_uid + ', type: ' + str(
#                 self.dict_of_header_objects[key].print_type()) + ', text: "' + str(
#                 self.dict_of_header_objects[key].text) + '", visible conditions: "' + str(
#                 self.dict_of_header_objects[key].visible_conditions)[:10] + '"\n'
#         return temp_str
#
#     def add_header_object(self, page_header_object):
#         '''
#         :param reference_object_for_assertion:
#         :param page_header_object:
#         :return: None
#         '''
#         assert isinstance(page_header_object, self.reference_object_for_assertion)
#         self.dict_of_header_objects[page_header_object.question_uid] = page_header_object
#
#     def drop_header_object(self, uid):
#         assert isinstance(uid, str)
#         if uid in self.dict_of_header_objects:
#             self.dict_of_header_objects.pop(uid)
#         else:
#             raise KeyError('UID ' + str(uid) + 'not found!')
#
#
# class PageHeader(Header):
#     def __init__(self):
#         super().__init__(PageHeaderObject)
#
#
# class QuestionHeader(Header):
#     def __init__(self):
#         super().__init__(QuestionHeaderObject)
#
#
# class ResponseDomain(UniqueObject):
#     def __init__(self, uid, variable, visible_condition):
#         super().__init__(uid)
#         self.variable = None
#         self.change_variable(variable)
#         self.visible_condition = None
#         self.change_visible_conditions(visible_condition)
#         self.dict_of_items = {}
#         self.dict_of_answeroptions = {}
#
#     def add_item(self, item):
#         assert isinstance(item, Item)
#         if self.dict_of_answeroptions != {}:
#             raise KeyError('Answeroptions already present while trying to add an Item - both are not allowed next to '
#                            'each other at this level!')
#         if item.uid not in self.dict_of_items:
#             self.dict_of_items[item.uid] = item
#         else:
#             raise KeyError('duplicate uid of item: "' + str(item.uid) + '" already present!')
#
#     def add_answeroption(self, answeroption):
#         assert isinstance(answeroption, AnswerOption)
#         if self.dict_of_items != {}:
#             raise KeyError('Items already present while trying to add an AnswerOption - both are not allowed next to '
#                            'each other at this level!')
#         if answeroption.uid not in self.dict_of_answeroptions:
#             self.dict_of_answeroptions[answeroption.uid] = answeroption
#         else:
#             raise KeyError('duplicate uid of item: "' + str(answeroption.uid) + '" already present!')
#
#     def drop_answeroption(self, uid):
#         if uid in self.dict_of_answeroptions:
#             self.dict_of_answeroptions.pop(uid)
#         pass
#
#     def drop_item(self, uid):
#         if uid in self.dict_of_items:
#             self.dict_of_items.pop(uid)
#         pass
#
#     def change_variable(self, variable):
#         assert isinstance(variable, str)
#         self.variable = variable
#
#     def change_visible_conditions(self, visible_conditions):
#         assert isinstance(visible_conditions, str)
#         self.visible_condition = visible_conditions
#
#
# class Item(UniqueObject):
#     def __init__(self, uid):
#         super().__init__(uid)
#         self.dict_of_answeroptions = {}
#         pass
#
#     def __str__(self):
#         temp_str = 'item uid: ' + str(self.uid) + '\n'
#         for key in self.dict_of_answeroptions.keys():
#             temp_str += 'uid: ' + self.dict_of_answeroptions[key].question_uid + ', label: ' + str(
#                 self.dict_of_answeroptions[key].labeltext) + ', value: ' + str(
#                 self.dict_of_answeroptions[key].var_value) + ', missing: ' + str(
#                 self.dict_of_answeroptions[key].missing) + '\n'
#         return temp_str
#
#     def add_answeroption(self, answeroption):
#         assert isinstance(answeroption, AnswerOption)
#         if answeroption.uid not in self.dict_of_answeroptions:
#             self.dict_of_answeroptions[answeroption.uid] = answeroption
#         else:
#             raise KeyError('duplicate uid of answeroptions: "' + str(answeroption.uid) + '" already present!')
#
#     def drop_answeroption(self):
#         pass
#
#
# class AnswerOption(UniqueObject):
#     def __init__(self, uid, value, labeltext=None, missing=False):
#         super().__init__(uid)
#         self.labeltext = None
#         self.value = None
#         self.missing = False
#         self.change_labeltext(labeltext)
#         self.change_value(value)
#         self.set_missing(missing)
#         pass
#
#     def __str__(self):
#         return 'label: "' + str(self.labeltext) + '", value: ' + str(self.value) + ', missing: ' + str(self.missing)
#
#     def change_labeltext(self, labeltext):
#         """
#         :param labeltext: string or none
#         :return: nothing
#         """
#         assert isinstance(labeltext, str) or labeltext is None
#         self.labeltext = labeltext
#
#     def change_value(self, value):
#         """
#         :param value: string value
#         :return: nothing
#         """
#         assert isinstance(value, str)
#         self.value = value
#
#     def set_missing(self, missing):
#         """
#         :param missing: boolean value
#         :return:
#         """
#         assert missing is True or missing is False
#         self.missing = missing
#
#
# class BodyQuestionTypes:
#     def __init__(self):
#         self.list_of_available_question_types = [BodyCalendar, BodyComparison, BodyMatrixDouble, BodyMatrixMultipleChoice, BodyMatrixQuestionMixed, BodyMatrixQuestionSingleChoice, BodyQuestionOpen]
#         self.dict_of_question_tags = {}
#         self.dict_of_question_types = {}
#         for body_question_type_class in QuestionObject.__subclasses__():
#             self.dict_of_question_types[getattr(body_question_type_class, '__name__')] = body_question_type_class
#             # self.dict_of_question_tags[body_question_type_class.tag] = body_question_type_class
#
#     def __str__(self):
#         return str(self.dict_of_question_types.keys())
#
#
# class Questions:
#     def __init__(self):
#         self.dict_of_question_objects = {}
#
#     def add_question_object(self, question_object):
#         assert isinstance(question_object, tuple(QuestionObject.__subclasses__()))
#         assert question_object.question_uid not in self.dict_of_question_objects.keys()
#         self.dict_of_question_objects[question_object.question_uid] = question_object
#
#     def __str__(self):
#         print('Question Objects')
#         print(self.dict_of_question_objects)
#
#
# class QuestionObject(UniqueObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid)
#         self.variables = Variables()
#         self.header = QuestionHeader()
#         self.index = None
#         self.tag = None
#         self.set_tag(tag)
#         self.set_index(index)
#
#     def set_index(self, index):
#         assert isinstance(index, int)
#         self.index = index
#
#     def set_tag(self, tag):
#         assert(isinstance(tag, str))
#         if tag != '':
#             self.tag = tag
#
#
# class BodyQuestionCalendar(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyCalendar(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyComparison(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class Display(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyMatrixDouble(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyMatrixMultipleChoice(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         self.uid = uid
#         self.items = {}
#         self.visible_condition = None
#         pass
#
#     def add_item(self, item):
#         # self.item.uid = ""
#         pass
#
#     def list_vars(self):
#         pass
#
#
# class BodyMatrixQuestionMixed(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyMatrixQuestionOpen(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyMatrixQuestionSingleChoice(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyMultipleChoice(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyQuestionOpen(QuestionObject):
#     def __init__(self, uid, variable, text_type='text', prefix=None, postfix=None):
#         super().__init__(uid)
#         self.text_type = None
#         self.__allowed_text_types = ['grade', 'number', 'text']
#         self.type = None
#         self.change_text_type(text_type)
#         self.variable = None
#         self.set_variable(variable)
#         self.prefix = None
#         self.postfix = None
#         self.set_prefix(prefix)
#         self.set_postfix(postfix)
#
#     def set_prefix(self, prefix):
#         assert isinstance(prefix, str)
#         self.prefix = prefix
#
#     def set_postfix(self, postfix):
#         assert isinstance(postfix, str)
#         self.postfix = postfix
#
#     def set_variable(self, variable):
#         assert isinstance(variable, Variable)
#         self.variable = variable
#
#     def change_text_type(self, text_type):
#         assert isinstance(text_type, str)
#         if text_type in self.__allowed_text_types:
#             self.text_type = text_type
#         else:
#             raise ValueError('QuestionOpen: text type "' + str(text_type) + '" not allowed.')
#
#
# class BodyQuestionPretest(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodyQuestionSingleChoice(QuestionObject):
#     def __init__(self, uid, index, tag):
#         super().__init__(uid, index, tag)
#         pass
#
#
# class BodySection(UniqueObject):
#     def __init__(self, uid):
#         super().__init__(uid)
#
#
# class Unit(UniqueObject):
#     def __init__(self, uid):
#         super().__init__(uid)
#         pass
#
#
# class Trigger:
#     def __init__(self):
#         pass
#
#
# class Triggers:
#     def __init__(self):
#         pass
#
#     def add_trigger(self, trigger):
#         assert isinstance(trigger, Trigger)
#         pass
#
#
# class Transition:
#     def __init__(self, index, target, condition):
#         assert isinstance(index, int)
#         assert isinstance(target, str)
#         assert isinstance(condition, str) or condition is None
#
#         self.index = index
#         self.target = target
#         self.condition = condition
#         self.condition_python = None
#         self.condition_new = None
#
#
# class TransitionLabels:
#     def __init__(self):
#         self.targets = []
#         self.conditions = {}
#
#     def add_targets_and_conditions(self, target, index, condition):
#         assert isinstance(target, str) and isinstance(index, int) and isinstance(condition, str)
#         if target not in self.targets:
#             self.targets.append(target)
#             self.conditions[target] =  {index: condition}
#         else:
#             if index not in self.conditions[target]:
#                 self.conditions[target]['index'] = condition
#             else:
#                 raise KeyError('Target "' + target + '" already in dictionary!')
#
# class Transitions:
#     def __init__(self):
#         self.transitions = {}
#         self.transition_labels = TransitionLabels()
#
#     def add_transitions(self, transition):
#         assert isinstance(transition, Transition)
#         if transition.index not in self.transitions:
#             self.transitions[transition.index] = transition
#         else:
#             raise ValueError('Index "' + '" already present in self.transitions!')
#
#
# class Sources:
#     def __init__(self):
#         self.sources = []
#
#     def add_source(self, source):
#         assert isinstance(source, str)
#         if source not in self.sources:
#             self.sources.append(source)
#
#
# class Variable:
#     def __init__(self, varname, vartype, varplace=None):
#         self.__allowed_vartypes = ['boolean', 'singleChoiceAnswerOption', 'string', 'number']
#         self.__allowed_varplaces = ['body', 'triggers', None]
#         if isinstance(varname, str) and isinstance(vartype, str):
#             self.varname = varname
#             if vartype in self.__allowed_vartypes:
#                 self.vartype = vartype
#             else:
#                 raise ValueError('Vartype unknown/not allowed: ' + str(varname) + ', ' + str(vartype))
#         else:
#             raise TypeError('Input not of type string')
#
#         self.set_varplace(varplace=varplace, varname=varname)
#
#     def set_varplace(self, varplace, varname):
#         if isinstance(varplace, str) or varplace is None:
#             self.varplace = varplace
#             if varplace in self.__allowed_varplaces:
#                 self.varplace = varplace
#             else:
#                 raise ValueError('Varplace unknown/not allowed: ' + str(varname) + ', ' + str(varplace))
#         else:
#             raise TypeError('Input not of type string')
#         return self
#
#     def __str__(self):
#         return str(self.varname)
#
#
# class Variables:
#     def __init__(self):
#         self.variables = {}
#
#     def __len__(self):
#         return len(self.variables)
#
#     def __str__(self):
#         return str(self.list_details_str())
#
#     def dict_details(self):
#         """
#         :return: dictionary of {varname: vartype}
#         """
#         dict_tmp = {}
#         for var in self.variables:
#             dict_tmp[var.varname] = self.variables[var].vartype
#         return dict_tmp
#
#     def list_all_vars(self):
#         return [var.varname for var in self.variables.values()]
#
#     def list_all_vartypes(self):
#         return [var.vartype for var in self.variables.values()]
#
#     def list_details_str(self):
#         return [str(self.variables[var].varname) + ': ' + str(self.variables[var].vartype) for var in self.variables]
#
#     def add_variable(self, variable_object, replace=False):
#         if isinstance(variable_object, Variable):
#             if variable_object.varname not in [self.variables[var].varname for var in self.variables]:
#                 self.variables[variable_object.varname] = variable_object
#             else:
#                 if not replace:
#                     # ToDo: error handling! maybe error message: yes/no ??
#                     # raise ValueError('Variable name exists already!')
#                     print("Variable " + str(variable_object.varname) + " already exists.")
#         else:
#             raise TypeError('Input not of type Variable')
#
#     def delete_variable(self, varname):
#         if isinstance(varname, str):
#             tmp_list = [self.variables[var].varname for var in self.variables]
#             tmp_var_list = self.variables.keys()
#             if varname in tmp_list:
#                 for var in tmp_var_list:
#                     if var.varname is varname:
#                         self.variables.pop(var)
#             else:
#                 raise ValueError('Varname not found!')
#         else:
#             raise TypeError('Input was not of type string!')
#
#     def check_if_vartype(self, varname, vartype):
#         if isinstance(varname, str) and isinstance(vartype, str):
#             if varname in [self.variables[var].varname for var in self.variables]:
#                 for var in [self.variables[var] for var in self.variables if var.varname is varname]:
#                     print(str(var))
#
#                     return var.vartype is vartype
#             else:
#                 raise ValueError('Varname not found!')
#         else:
#             raise TypeError('Input was not of type string!')
#
#
# class QmlPages:
#     def __init__(self):
#         self.pages = {}
#
#     def add_page(self, qmlpage, replace=False):
#         assert isinstance(qmlpage, QmlPage)
#         if qmlpage.uid in self.pages.keys():
#             if not replace:
#                 raise KeyError('Page already exists and overwrite is False.')
#             else:
#                 ('Page "' + qmlpage.uid + '" will be replaced.')
#                 self.pages[qmlpage.uid] = qmlpage
#         else:
#             self.pages[qmlpage.uid] = qmlpage
#
#     def drop_page(self, uid):
#         assert isinstance(uid, str)
#         if uid in self.pages:
#             self.pages.pop(uid)
#         else:
#             raise ValueError('Pagename "' + str(uid) + '" not found in self.pages!')
#
#     def list_of_all_pagenames(self):
#         tmp_list = []
#         for key in self.pages:
#             tmp_list.append(key)
#         return tmp_list
#
#
# class DuplicateVariables(Variables):
#     def __init__(self):
#         super().__init__()
#
#
# class QmlPage(UniqueObject):
#     def __init__(self, uid, declared=True):
#         super().__init__(uid)
#         self.declared = declared
#
#         self.header = PageHeader()
#         self.transitions = Transitions()
#         self.variables = Variables()
#         self.triggers = Triggers()
#         self.sources = Sources()
#         self.duplicate_variables = DuplicateVariables()
#         self.questions = Questions()
#
#     def add_sources(self, source):
#         self.sources.add_source(source)
#
#     def add_transition(self, transition):
#         self.transitions.add_transitions(transition)
#
#     def add_variable(self, variable):
#         self.variables.add_variable(variable)
#
#     def add_trigger(self, trigger):
#         self.triggers.add_trigger(trigger)
#
#     def add_header(self, header_text):
#         self.header.add_header_object(header_text)
#
#     def __translate_transition_condition_to_python_syntax(self):
#         regex1 = re.compile(r'==')  # 'is'
#         regex2 = re.compile(r'!=')  # 'is not'
#         regex3 = re.compile(r'gt')  # '>'
#         regex4 = re.compile(r'ge')  # '>='
#         regex5 = re.compile(r'lt')  # '<'
#         regex6 = re.compile(r'le')  # '<='
#         regex7 = re.compile(r'zofar.asNumber')  # 'int'
#         regex8 = re.compile(r'zofar.isMissing\(([a-zA-Z0-9\-_]+)\)')  # '(\1 is None)'
#         regex9 = re.compile(r'.value')  # 'is True'
#         regex10 = re.compile(r'!')  # 'not'
#         regex11 = re.compile(r' AND ')  # ' and '
#         regex12 = re.compile(r' OR ')  # ' or '
#
#         if self.transitions is not {}:
#             for key in self.transitions.keys():
#                 if self.transitions.transitions[key]['condition'] is None:
#                     self.transitions.transitions[key]['condition_python'] = 'True'
#                 else:
#                     self.transitions.transitions[key]['condition_python'] = regex1.sub('is', self.transitions.transitions[key]['condition'])
#                     self.transitions.transitions[key]['condition_python'] = regex2.sub('is not',
#                                                                            self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex3.sub('>', self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex4.sub('>=', self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex5.sub('<', self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex6.sub('<=', self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex7.sub('int', self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex8.sub('(\g<1> is None)',
#                                                                            self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex9.sub('is True',
#                                                                            self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex10.sub('not ',
#                                                                             self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex11.sub(' and ',
#                                                                             self.transitions.transitions[key]['condition_python'])
#                     self.transitions.transitions[key]['condition_python'] = regex12.sub(' or ',
#                                                                             self.transitions.transitions[key]['condition_python'])

