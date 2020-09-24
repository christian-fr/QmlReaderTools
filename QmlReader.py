__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.2.1"
__status__ = "Prototype"
__name__ = "QmlReader"

# last edited: 2020-04-16
from typing import Type, Any

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

        self.title = self.extract_title()

        self.questionnaire = QuestionnaireObject.QuestionnaireObject(file=self.file, title=self.title)

        self.extract_declared_variables_to_questionnaire_object()

        self.page_sources_dict = {}
        self.extract_pages_to_page_sources_dict()

        self.iterate_through_all_page_objects_in_page_sources_dict()

        self.extract_transitions_from_qml_page_source()

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
            self.questionnaire.add_variables_to_declared_variables_dict(QuestionnaireElements.VariableObject(name_string=self.root.variables.variable[i].attrib["name"], var_type_string=self.root.variables.variable[i].attrib["type"]))

    def extract_pages_to_page_sources_dict(self):
        self.logger.info("extract_pages_to_dict_of_pages")
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            self.page_sources_dict[tmp_page_uid] = tmp_qml_page_source

    def iterate_through_all_page_objects_in_page_sources_dict(self):
        tmp_count = 0
        for page_uid, page_source_object in self.page_sources_dict.items():
            print(page_uid)
            print(type(page_uid))
            print('#'*100)
            self.questionnaire.add_page(QuestionnaireElements.PageObject(uid_value=page_uid, index_value=tmp_count, declared=True))
            self.extract_transitions_from_qml_page_source(page_source_object=page_source_object, page_uid_value=page_uid)
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

                    self.questionnaire.get_page_from_uid(page_uid=page_uid_value).add_transition(QuestionnaireElements.TransitionObject(page_uid_value=page_uid_value, target_page_uid_value=tmp_target, index_value=tmp_index, condition_string=tmp_condition))
                    # self.questionnaire.pages.pages[page_uid].transitions.add_transitions(QuestionnaireObject.Transition(index=tmp_index, target=tmp_target, condition=tmp_condition))




xml_file = r'qml/questionnaireNacaps2018-2.xml'
x = QmlReader(xml_file)
t = x.questionnaire.declared_variables_dict['s_split_poli1']
