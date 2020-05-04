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

    def __init__(self, file, create_graph=False, draw=False, truncate=False):
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
        logging.info("QmlReader object is done.")

    def list_of_variables_from_pages(self):
        pass

    def list_of_pages(self):
        return list(self.questionnaire.pages.pages.keys())

    def create_graph(self):
        """
        deprecated since version 0.2.0
        is implemented in Questionnaire.Questionnaire
        :param
        :return:
        """
        logging.info("create_graph")
        self.transitions_to_nodes_edges()
        self.init_pgv_graph()
        self.prepare_pgv_graph()

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
            list_variables_per_page = []
            if hasattr(self.root.page[pagenr], 'body'):
                for i in self.root.page[pagenr].body.iterdescendants():
                    try:
                        tmp_varname = i.attrib['variable']
                        tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(varplace='body', varname=tmp_varname)
                        if tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].variables.list_all_vars() and tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                            self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                        else:
                            logging.info('Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(tmp_pagename) + '". Possible duplicate.')
                            self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(tmp_var_object, replace=True)
                    except KeyError:
                        pass

    def extract_variables_from_pages_triggers(self):
        logging.info("extract_variables_from_pages_triggers")
        for pagenr in range(0, len(self.root.page)):
            tmp_pagename = self.root.page[pagenr].attrib['uid']
            list_variables_per_page = []
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
        #for i in range(0, len(self.root.page)):
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

    def extract_headers_from_question(self):
        logging.info("extract_headers_from_question")
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

    # ToDo: move method to Questionnaire.py - and fix implementation
    def transitions_to_nodes_edges(self, truncate=False):
        """
        deprecated since version 0.2.0!
        is implemented in Questionnaire.Questionnaire
        :param
        :return:
        """
        logging.info("transitions_to_nodes_edges")
        print("transitions_nodes_to_edges")
        self.questionnaire.create_readable_conditions()

        for page in self.questionnaire.pages.pages.values():
            self.DiGraph.add_node(page.uid)  # create nodes
            cnt = 0
            dict_transitions = {}
            for transition in page.transitions.transitions.values():
                if transition.condition is not None:
                    if transition.target in dict_transitions.keys():
                        dict_transitions[transition.target] = dict_transitions[transition.target] + ' |\n(' + '[' + str(cnt) + '] ' + transition.condition_new + ']' + ')'
                        self.DiGraph.add_edge(page.uid, transition.target, label='[' + str(cnt) + '] ' + dict_transitions[transition.target])
                    else:
                        dict_transitions[transition.target] = '(' + '[' + str(cnt) + '] ' + transition.condition_new + ')'

                    self.DiGraph.add_edge(page.uid, transition.target, label=dict_transitions[transition.target])

                else:
                    if transition.target in dict_transitions.keys():
                        self.DiGraph.add_edge(page.uid, transition.target, label='')
                    else:
                        if cnt is 0:
                            self.DiGraph.add_edge(page.uid, transition.target, label='')
                        if cnt is not 0:
                            self.DiGraph.add_edge(page.uid, transition.target, label='[' + str(cnt) + ']')

                cnt = cnt + 1


    # def node_labels(self):
    #    labeldict = {}
    #    for page in self.questionnaire.pages.pages.values():
    #        labeldict[page.uid] = page.uid + '\n[' + ['\n'.join(varname) for varname in page.variables.list_all_vars()]
    #    return labeldict

    def init_pgv_graph(self, graph_name='graph'):
        """
        deprecated since version 0.2.0!
        is implemented in Questionnaire.Questionnaire
        :param
        :return:
        """
        logging.info("init_pgv_graph")
        self.pgv_graph = nx.nx_agraph.to_agraph(self.DiGraph)

        t = time.localtime()
        timestamp = time.strftime('%Y-%m-%d_%H-%M', t)

        self.pgv_graph.node_attr['shape'] = 'box'
        self.pgv_graph.graph_attr['label'] = 'title: ' + self.title + '\nfile: ' + self.questionnaire.filename + '\n timestamp: ' + timestamp
        self.pgv_graph.layout("dot")

    def prepare_pgv_graph(self):
        """
        deprecated since version 0.2.0!
        is implemented in Questionnaire.Questionnaire
        :param
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
        self.logger.info('output_png: ' + str(path.join(output_folder, filename + '.gml')))
        self.draw_pgv_graph(path.join(output_folder, filename + '.png'))

    def draw_pgv_graph(self, output_file='output_file.png'):
        self.pgv_graph.draw(output_file)
