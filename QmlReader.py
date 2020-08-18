__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.2.0"
__status__ = "Prototype"
__name__ = "QmlReader"

# last edited: 2020-04-16

import lxml
from lxml import objectify
import networkx as nx
import logging
import Questionnaire
from os import path
import time
import errno
from os import listdir, mkdir


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
        self.DiGraph = nx.DiGraph()

        with open(file, 'rb') as f:
            self.logger.info('reading file: ' + str(file))
            self.data = f.read()

        self.root = objectify.fromstring(self.data)

        self.questionnaire = Questionnaire.Questionnaire(file=file)

        self.title = 'Survey'
        self.set_title()
        self.extract_declared_variables()

        self.tmp_dict_of_pages = {}
        self.pgv_graph = None
        self.extract_pages_into_tmp_dict()
        self.extract_pages_to_self()

        self.extract_variables_from_pages_body()
        self.extract_variables_from_pages_triggers()

        self.extract_headers_and_questions_from_pages()
        logging.info("QmlReader object is done.")

    def list_of_variables_from_pages(self):
        pass

    def list_of_pages(self):
        return list(self.questionnaire.pages.pages.keys())

    # def create_graph(self):
    #     """
    #     deprecated since version 0.2.0
    #     is implemented in Questionnaire.Questionnaire
    #     :param
    #     :return:
    #     """
    #     logging.info("create_graph")
    #     self.transitions_to_nodes_edges()
    #     self.init_pgv_graph()
    #     self.prepare_pgv_graph()

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
        logging.info("set_title")
        self.title = self.extract_title()

    def extract_title(self):
        logging.info("extract_title")
        return self.root.name.text

    def extract_variables_from_pages_body(self):
        logging.info("extract_variables_from_pages_body")
        for pagenr in range(0, len(self.root.page)):
            tmp_pagename = self.root.page[pagenr].attrib['uid']
            if hasattr(self.root.page[pagenr], 'body'):
                for i in self.root.page[pagenr].body.iterdescendants():
                    if 'variable' in i.attrib:
                        tmp_varname = i.attrib['variable']
                        tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(varplace='body', varname=tmp_varname)
                        if tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].variables.list_all_vars() and tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                            self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                        else:
                            logging.info('Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(tmp_pagename) + '". Possible duplicate.')
                            self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(tmp_var_object, replace=True)

    def extract_variables_from_pages_triggers(self):
        logging.info("extract_variables_from_pages_triggers")
        for pagenr in range(0, len(self.root.page)):
            tmp_pagename = self.root.page[pagenr].attrib['uid']
            if hasattr(self.root.page[pagenr], 'triggers'):
                for i in self.root.page[pagenr].triggers.iterdescendants():
                    try:
                        tmp_varname = i.attrib['variable']
                        tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(varplace='triggers', varname=tmp_varname)
                        if tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].variables.list_all_vars() and tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                            self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                        else:
                            logging.info('Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(tmp_pagename) + '". Possible duplicate.')
                            self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(tmp_var_object, replace=True)
                    except KeyError:
                        pass

    def extract_declared_variables(self):
        logging.info("extract_declared_variables")
        for i in range(0, len(self.root.variables.variable)):
            # print(self.questionnaire.filename)
            # print(self.root.variables.variable[i].attrib['name'])
            self.questionnaire.variables.add_variable(Questionnaire.Variable(self.root.variables.variable[i].attrib["name"], self.root.variables.variable[i].attrib["type"]))

    def extract_pages_into_tmp_dict(self):
        logging.info("extract_pages_into_tmp_dict")
        for i in range(0, len(self.root.page)):
            self.tmp_dict_of_pages[self.root.page[i].attrib['uid']] = self.root.page[i]

    def extract_pages_to_self(self):
        logging.info("extract_pages_to_self")
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            self.questionnaire.pages.add_page(Questionnaire.QmlPage(tmp_page_uid, declared=True))
            self.extract_transitions_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)

        # ToDo: when method self.extract_sources_from_questionnaire() is moved to Questionnaire.py: fix this call
        # for i in range(0, len(self.root.page)):
        #    self.extract_sources_from_questionnaire()

    def extract_transitions_from_qml_page_source(self, qml_source_page, uid):
        logging.info("extract_transitions_from_qml_page_source from page: " + str(uid))
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

    def extract_questions_from_pages(self):
        logging.info("extract_questions_from_pages")
        pass

    def extract_headers_and_questions_from_pages(self):
        logging.info("extract_headers_from_pages")
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            self.extract_page_headers_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)
            self.extract_question_objects_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)

    def extract_page_headers_from_qml_page_source(self, qml_source_page, page_uid):
        logging.info("extract_page_headers_from_page_sources; uid: " + str(page_uid))
        assert isinstance(qml_source_page, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid, str)
        if hasattr(qml_source_page, 'header'):
            logging.info("  found page header")
            i = -1
            if len([i for i in qml_source_page.header.iterchildren()]) > 0:
                logging.info("  page header has length > 0")
                for header in qml_source_page.header.iterchildren():
                    tmp_object = None
                    i += 1
                    tmp_index = i
                    logging.info("  page header object - index: " + str(i))
                    tmp_uid = header.attrib['uid']
                    logging.info("  page header object - uid: " + str(tmp_uid))
                    if header.text is not None:
                        tmp_text = header.text
                    else:
                        tmp_text = ''
                    logging.info("  page header object - text: '" + str(tmp_text) + "'")

                    if 'visible' in header.attrib:
                        tmp_visible_conditions = header.attrib['visible']
                        logging.info("  found visible condition: " + str(tmp_visible_conditions))
                    else:
                        tmp_visible_conditions = None
                        logging.info("  found visible condition: None")

                    tmp_tag = header.tag[header.tag.rfind('}') + 1:]
                    logging.info("  found tag: '" + str(tmp_tag) + "'")
                    tmp_object = Questionnaire.PageHeaderObject(uid=tmp_uid, tag=tmp_tag, text=tmp_text, index=tmp_index, visible_conditions=tmp_visible_conditions)

                    logging.info("  adding PageHeaderObject: '" + str(tmp_object.tag) + "' to page: " + str(page_uid))
                    self.questionnaire.pages.pages[page_uid].header.add_header_object(tmp_object)

            else:
                logging.info("  page header has length == 0 and will be ignored")

        else:
            logging.info("  no page header found")

    def extract_question_objects_from_qml_page_source(self, qml_source_page, page_uid):
        logging.info("extract_question_objects_from_qml_page_source; uid: " + str(page_uid))
        assert isinstance(qml_source_page, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid, str)
        if hasattr(qml_source_page, 'body'):
            i = 0
            logging.info('  body found on page "' + str(page_uid) + '".')
            tmp_body_uid = qml_source_page.body.attrib['uid']
            for element in qml_source_page.body.iterchildren():
                tmp_tag = element.tag[element.tag.rfind('}') + 1:]

                if tmp_tag == 'calendar':
                    tmp_question_header_object = self.extract_question_header_from_qml_element_source(element, page_uid)
                    tmp_index = i
                    i += 1
                if tmp_tag == 'comparison':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'display':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'matrixDouble':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'matrixMultipleChoice':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'matrixQuestionMixed':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'matrixQuestionOpen':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'matrixQuestionSingleChoice':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'multipleChoice':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'questionOpen':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'questionPretest':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'questionSingleChoice':
                    tmp_index = i
                    i += 1
                    # ToDo
                    ## self.questionnaire.pages.pages[page_uid].questions.add_question_object()

                    (self.extract_question_header_from_qml_element_source(element, page_uid))
                if tmp_tag == 'section':
                    tmp_index = i
                    i += 1
                if tmp_tag == 'section':
                    tmp_index = i
                    i += 1
        pass

    def extract_response_domains_from_question(self):
        logging.info("extract_response_domains_from_question")
        pass

    def extract_items_from_response_domain(self):
        logging.info("extract_items_from_response_domain")
        pass

    def extract_answeroptions_from_response_domain(self):
        logging.info("extract_answeroptions_from_response_domain")
        pass

    # ToDo: move this method to questionnaire, fix the ToDos below
    def extract_sources_from_questionnaire(self):
        logging.info("extract_sources_from_questionnaire")
        tmp_dict_of_additional_pages = {}
        for page in self.questionnaire.pages.pages.values():
            for transition in page.transitions.transitions.values():
                # ToDo: (see below) the following is just a workaround until option "combine" is implemented issue#9
                if transition.target in self.questionnaire.pages.pages.keys():
                    self.questionnaire.pages.pages[transition.target].sources.add_source(page.uid)
                else:
                    tmp_dict_of_additional_pages[transition.target] = page.uid
        # ToDo: (see above) the following is just a workaround until option "combine" is implemented issue#9
        for newpagename in tmp_dict_of_additional_pages.keys():
            self.questionnaire.pages.add_page(Questionnaire.QmlPage(newpagename, declared=False))
            self.questionnaire.pages.pages[newpagename].sources.add_source(tmp_dict_of_additional_pages[newpagename])

    def extract_triggers_from_pages(self):
        logging.info("extract_triggers_from_pages")
        pass

    def extract_question_from_qml_page(self, qml_page):
        logging.info("extract_question_from_qml_page")
        assert isinstance(qml_page, lxml.objectify.ObjectifiedElement)

    def extract_triggers_from_qml_page(self, qml_page):
        logging.info("extract_triggers_from_qml_page")
        assert isinstance(qml_page, lxml.objectify.ObjectifiedElement)

    def draw_pgv_graph(self, output_file='output_file.png'):
        self.pgv_graph.draw(output_file)

    def extract_question_header_from_qml_element_source(self, qml_source_element, page_uid):
        flag_question = False
        flag_instruction = False
        flag_introduction = False
        tmp_header = Questionnaire.QuestionHeader()
        if hasattr(qml_source_element, 'header'):
            for header_question_object in qml_source_element.header.iterchildren():
                j = 0
                if hasattr(header_question_object, 'tag'):
                    if header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'question':
                        logging.info('  tag "question" found')
                    elif header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'instruction':
                        logging.info('  tag "instruction" found')
                    elif header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'introduction':
                        logging.info('  tag "introduction" found')
                    elif header_question_object.tag == 'comment':
                        logging.info('  xml comment found - will be ignored')
                        continue
                    else:
                        logging.info('  unexpected tag found: "' + header_question_object.tag + '" in header on page ' + str(page_uid))
                        raise ValueError('  unexpected tag found: "' + header_question_object.tag + '" in header on page ' + str(page_uid))

                tmp_index = j
                j += 1

                tmp_uid = header_question_object.attrib['uid']
                tmp_text = header_question_object.text
                if 'visible' in header_question_object.attrib:
                    tmp_visible = header_question_object.attrib['visible']
                else:
                    tmp_visible = None
                tmp_tag = header_question_object.tag[header_question_object.tag.rfind('}') + 1:]
                tmp_header.add_header_object(Questionnaire.QuestionHeaderObject(uid=tmp_uid, text=tmp_text, tag=tmp_tag, index=tmp_index, visible_conditions=tmp_visible))
        return tmp_header


           # for header_element in qml_source_element.header:
           #     tmp_uid = header_element.uid
           #     tmp_text = header_element.text
           #     tmp_tag = header.tag[header.tag.rfind('}') + 1:]
           #     tmp_index =
           #     tmp_page_header_object = Questionnaire.PageHeaderObject()
           #     tmp_header.add_header_object()
        pass

