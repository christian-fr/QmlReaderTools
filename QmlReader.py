__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.3.0"
__status__ = "Prototype"
__name__ = "QmlReader"

import lxml
from lxml import objectify
import networkx as nx
import logging
import QuestionnaireObject
from os import path
import time
import errno
from os import listdir, mkdir
import QuestionnaireElements
import QmlExtractionFunctions


class QmlReader:
    """
    Class for Reading and extracting elements from QML-Files.
    """

    def __init__(self, file):
        self.file = file
        self.tmp = []
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)
        self.logger.info('starting up QmlReader')

        with open(file, 'rb') as f:
            self.logger.info('reading file: ' + str(file))
            self.data = f.read()

        self.root = objectify.fromstring(self.data)

        comments = self.root.xpath('//comment()')

        for c in comments:
            p = c.getparent()
            p.remove(c)

        self.title = self.extract_title()

        self.questionnaire = QuestionnaireObject.QuestionnaireObject(file=self.file, title=self.title)

        self.extract_declared_variables_to_questionnaire_object()

        self.page_sources_dict = {}
        self.extract_pages_to_page_sources_dict()

        self.iterate_through_all_page_objects_in_page_sources_dict()

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title_string):
        assert isinstance(title_string, str)
        self.__title = title_string

    def list_of_variables_from_pages(self):
        pass

    def list_of_pages(self):
        return list(self.questionnaire.get_all_pages_list())

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

    def extract_title(self):
        self.logger.info("extract_title")
        return self.root.name.text

    def extract_declared_variables_to_questionnaire_object(self):
        self.logger.info("extract_declared_variables")
        for i in range(0, len(self.root.variables.variable)):
            # print(self.questionnaire.filename)
            # print(self.root.variables.variable[i].attrib['name'])
            self.questionnaire.add_variables_to_declared_variables_dict(
                QuestionnaireElements.VariableObject(name_string=self.root.variables.variable[i].attrib["name"],
                                                     var_type_string=self.root.variables.variable[i].attrib["type"]))

    def extract_pages_to_page_sources_dict(self):
        self.logger.info("extract_pages_to_dict_of_pages")
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            self.page_sources_dict[tmp_page_uid] = tmp_qml_page_source

    def iterate_through_all_page_objects_in_page_sources_dict(self):
        tmp_count = 0
        for page_uid, page_source_object in self.page_sources_dict.items():
            self.questionnaire.add_page(
                QuestionnaireElements.PageObject(uid_value=page_uid, index_value=tmp_count, declared=True))
            self.extract_transitions_from_qml_page_source(page_source_object=page_source_object,
                                                          page_uid_value=page_uid)
            self.extract_page_headers_from_qml_page_source(page_source_object=page_source_object,
                                                           page_uid_value=page_uid)
            self.extract_questions_and_sections_from_qml_page_source(page_source_object=page_source_object,
                                                                     page_uid_value=page_uid)
            tmp_count += 1

    def extract_transitions_from_qml_page_source(self, page_source_object, page_uid_value):
        self.logger.info("extract_transitions_from_qml_page_source from page: " + str(page_uid_value))
        assert isinstance(page_source_object, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid_value, str)
        if hasattr(page_source_object, 'transitions'):
            if hasattr(page_source_object.transitions, 'transition'):
                i = -1
                for transition in page_source_object.transitions.transition:
                    i += 1
                    tmp_index = i
                    tmp_transition_dict = transition.attrib
                    tmp_target = tmp_transition_dict['target']
                    if 'condition' in tmp_transition_dict:
                        tmp_condition = tmp_transition_dict['condition']
                    else:
                        tmp_condition = None

                    self.questionnaire.get_page_from_uid(page_uid=page_uid_value).add_transition(
                        QuestionnaireElements.TransitionObject(page_uid_value=page_uid_value,
                                                               target_page_uid_value=tmp_target, index_value=tmp_index,
                                                               condition_string=tmp_condition))

    def extract_page_headers_from_qml_page_source(self, page_source_object, page_uid_value):
        self.logger.info("extract_page_headers_from_page_sources; uid: " + str(page_uid_value))
        assert isinstance(page_source_object, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid_value, str)
        if hasattr(page_source_object, 'header'):
            self.logger.info("  found page header")
            i = -1
            if len([i for i in page_source_object.header.iterchildren()]) > 0:
                self.logger.info("  page header has length > 0")
                for header in page_source_object.header.iterchildren():
                    # i += 1
                    # tmp_index = i
                    self.logger.info("  page header object - index: " + str(i))
                    if 'uid' not in header.attrib:
                        if hasattr(header, 'tag'):
                            if header.tag == 'comment':
                                self.logger.info("  found page header object: xml comment, ignored")
                        else:
                            self.logger.error(
                                '   found object in page header of ' + str(page_uid_value) + ' that could not be read.')
                        continue
                    tmp_uid = header.attrib['uid']
                    self.logger.info("  page header object - uid: " + str(tmp_uid))
                    if header.text is not None:
                        tmp_text = header.text
                    else:
                        tmp_text = ''
                    self.logger.info("  page header object - text: '" + str(tmp_text) + "'")

                    if 'visible' in header.attrib:
                        tmp_condition_string = header.attrib['visible']
                        self.logger.info("  found visible condition: " + str(tmp_condition_string))
                    else:
                        tmp_condition_string = None
                        self.logger.info("  found visible condition: None")

                    tmp_tag = QmlExtractionFunctions.get_tag_from_page_children_object(header)

                    self.logger.info("  found tag: '" + str(tmp_tag) + "'")

                    tmp_index = self.questionnaire.pages_dict[page_uid_value].get_page_object_next_index()

                    tmp_page_header_object = QuestionnaireElements.PageHeaderObject(uid_value=tmp_uid,
                                                                                    page_uid_value=page_uid_value,
                                                                                    page_header_type_string=tmp_tag,
                                                                                    page_header_text_string=tmp_text,
                                                                                    index_value=tmp_index,
                                                                                    condition_string=tmp_condition_string)

                    self.logger.info(
                        "  adding PageHeaderObject: '" + str(tmp_tag) + "' to page: " + str(page_uid_value))

                    self.questionnaire.get_page_from_uid(page_uid_value).add_page_header_object(tmp_page_header_object)

            else:
                self.logger.info("  page header has length == 0 and will be ignored")

        else:
            self.logger.info("  no page header found")

    def extract_questions_and_sections_from_qml_page_source(self, page_source_object, page_uid_value):
        self.logger.info("extract_page_headers_from_page_sources; uid: " + str(page_uid_value))
        assert isinstance(page_source_object, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid_value, str)

        if hasattr(page_source_object, 'body'):
            tmp_page_body_children_objects_list = [child_object for child_object in
                                                   page_source_object.body.iterchildren()]

            for child_object in tmp_page_body_children_objects_list:

                tmp_tag = QmlExtractionFunctions.get_tag_from_page_children_object(child_object)
                self.logger.info("  found tag: '" + str(tmp_tag) + "'")
                if tmp_tag == 'comment':
                    self.logger.info("  found page body object: xml comment, ignored")
                    continue

                elif tmp_tag == 'section':
                    self.logger.info("  found page body object: section")

                    print('#### section not yet implemented, passing...')

                else:
                    self.logger.info("  found tag: '" + str(tmp_tag) + "'")

                    tmp_index = self.questionnaire.pages_dict[page_uid_value].get_page_object_next_index()

                    tmp_question_uid = QmlExtractionFunctions.get_uid_attrib_of_source_object(child_object)

                    if tmp_question_uid is None:
                        raise KeyError(
                            '   element with tag: "{0}" on page: "{1}" does not seem to have a UID'.format(tmp_tag,
                                                                                                           page_uid_value))

                    if tmp_tag == 'questionSingleChoice':
                        tmp_question_header_objects_list = QmlExtractionFunctions.get_question_header_objects_list(
                            question_source_object=child_object, page_uid_value=page_uid_value)

                        # get answer_options_list and unit_objects_list
                        tmp_answer_option_objects_list, tmp_unit_objects_list = QmlExtractionFunctions.get_question_answer_options_objects_unit_objects_list(
                            question_source_object=child_object, page_uid_value=page_uid_value,
                            question_uid_value=tmp_question_uid)

                        tmp_condition_string = None

                        tmp_page_body_object = QuestionnaireElements.QuestionSingleChoiceObject(
                            uid_value=tmp_question_uid,
                            page_uid_value=page_uid_value,
                            index_value=tmp_index,
                            answer_option_objects_list=tmp_answer_option_objects_list,
                            question_header_objects_list=tmp_question_header_objects_list,
                            condition_string=tmp_condition_string, list_of_units=tmp_unit_objects_list)

                        self.questionnaire.pages_dict[page_uid_value].add_page_body_object(tmp_page_body_object)
                    elif tmp_tag == 'multipleChoice':
                        continue
                    elif tmp_tag == 'questionOpen':
                        tmp_question_header_objects_list = QmlExtractionFunctions.get_question_header_objects_list(
                            question_source_object=child_object, page_uid_value=page_uid_value)

                        QmlExtractionFunctions.extract_question_open_object_from_source_object_or_return_error(source_object=child_object,
                                                                                                               page_uid_value=page_uid_value,
                                                                                                               index_value=tmp_index,
                                                                                                               outer_uid_value=None)

                    elif tmp_tag == 'matrixQuestionSingleChoice':
                        continue
                    elif tmp_tag == 'comparison':
                        continue
                    else:
                        raise NotImplementedError('   handling for tag: "{0}" not yet implemented.'.format(tmp_tag))

    def extract_triggers_from_qml_page_source(self, page_source_object, page_uid_value):
        pass


xml_file = r'qml/questionnaireNacaps2018-2.xml'
x = QmlReader(xml_file)
t = x.questionnaire.declared_variables_dict['s_split_poli1']
