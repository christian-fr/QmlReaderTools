__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.5"
__status__ = "Prototype"
__name__ = "QmlReader"

# last edited: 2020-04-16

import lxml
from lxml import objectify
import networkx as nx
import logging
import Questionnaire


class QmlReader:
    """
    Class for Reading and extracting elements from QML-Files.

    self.dict_of_page_numbers:
        dictionary of: {lfdNr: 'pageNr/Uid'}

    self.dict_of_page_numbers_reversed:
        dictionary of: {'pageNr/Uid': lfdNr}

    """

    def __init__(self, file, create_graph=False, draw=False, truncate=False):
        self.tmp = []
        self.logger = logging.getLogger('debug')
        self.startup_logger(log_level=logging.DEBUG)
        self.logger.info('starting up QmlReader')
        self.DiGraph = nx.DiGraph()

        with open(file, 'rb') as f:
            self.logger.info('reading file: ' + str(file))
            self.data = f.read()

        self.root = objectify.fromstring(self.data)

        self.questionnaire = Questionnaire.Questionnaire(file)

        self.title = 'Survey'
        self.set_title()
        self.extract_declared_variables()


        self.tmp_dict_of_pages = {}
        self.extract_pages_into_tmp_dict()
        self.extract_pages_to_self()

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

    def set_title(self):
        self.title = self.extract_title()

    def extract_title(self):
        return self.root.name.text

    def extract_declared_variables(self):
        for i in range(0, len(self.root.variables.variable)):
            self.questionnaire.variables.add_variable(Questionnaire.Variable(self.root.variables.variable[i].attrib["name"], self.root.variables.variable[i].attrib["type"]))

    def extract_pages_to_self(self):
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            self.questionnaire.pages.add_page(Questionnaire.QmlPage(tmp_page_uid))
            self.extract_transitions_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)





    def extract_questions_from_pages(self):
        pass

    def extract_headers_from_question(self):
        pass

    def extract_response_domains_from_question(self):
        pass

    def extract_items_from_response_domain(self):
        pass

    def extract_answeroptions_from_response_domain(self):
        pass


    def extract_triggers_from_pages(self):
        pass

    def extract_pages_into_tmp_dict(self):
        for i in range(0, len(self.root.page)):
            self.tmp_dict_of_pages[self.root.page[i].attrib['uid']] = self.root.page[i]

    def extract_transitions_from_qml_page_source(self, qml_source_page, uid):
        assert isinstance(qml_source_page, lxml.objectify.ObjectifiedElement)
        assert isinstance(uid, str)
        if hasattr(qml_source_page, 'transitions'):
            if hasattr(qml_source_page.transitions, 'transition'):
                i = -1
                for transition in qml_source_page.transitions.transition:
                    i += 1
                    tmp_index = i
                    tmp_transition_dict = transition.attrib
                    tmp_target = tmp_transition_dict['target']
                    if 'condition' in tmp_transition_dict:
                        tmp_condition = tmp_transition_dict['condition']
                    else:
                        tmp_condition = None

                    self.questionnaire.pages.pages[uid].transitions.add_transitions(Questionnaire.Transition(index=tmp_index, target=tmp_target, condition=tmp_condition))

    def extract_question_from_qml_page(self, qml_page):
        assert isinstance(qml_page, lxml.objectify.ObjectifiedElement)

    def extract_triggers_from_qml_page(self, qml_page):
        assert isinstance(qml_page, lxml.objectify.ObjectifiedElement)


