__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "0.2.6"
__status__ = "Prototype"
__name__ = "QmlReader"

# last edited: 2020-04-16

import html
import lxml
from lxml import objectify, etree
import logging
from qrt.util import questionnaire
import re


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
        # self.DiGraph = nx.DiGraph()

        with open(file, 'rb') as f:
            self.logger.info('reading file: ' + str(file))
            self.data = f.read()

        self.root = objectify.fromstring(self.data)

        self.title = None
        self.set_title()
        self.questionnaire = questionnaire.Questionnaire(file=self.file, title=self.title)

        self.extract_declared_variables()

        self.tmp_dict_of_pages = {}
        # self.pgv_graph = None
        # self.extract_pages_into_tmp_dict()
        self.extract_pages_to_self()
        self.extract_transitions_to_self()

        self.extract_variables_from_pages_body()
        self.extract_variables_from_pages_triggers()

        self.extract_headers_and_questions_from_pages()
        self.logger.info("QmlReader object is done.")

    def list_of_variables_from_pages(self):
        pass

    def list_of_pages(self):
        return list(self.questionnaire.pages.pages.keys())

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
        self.logger.info("set_title")
        self.title = self.extract_title()

    def extract_title(self):
        self.logger.info("extract_title")
        return self.root.name.text

    def extract_variables_from_pages_body(self):
        self.logger.info("extract_variables_from_pages_body")
        for pagenr in range(0, len(self.root.page)):
            tmp_pagename = self.root.page[pagenr].attrib['uid']
            if hasattr(self.root.page[pagenr], 'body'):
                for element in self.root.page[pagenr].body.iterdescendants():
                    if 'variable' in element.attrib:  # ToDo: if condition added just for debugging - remove later!
                        tmp_varname = element.attrib['variable']
                        if tmp_varname in self.questionnaire.variables.variables.keys():
                            tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(
                                varplace='body', varname=tmp_varname)
                            if tmp_varname not in self.questionnaire.pages.pages[
                                tmp_pagename].variables.list_all_vars() and tmp_varname not in \
                                    self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                                self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                            else:
                                self.logger.info(
                                    'Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(
                                        tmp_pagename) + '". Possible duplicate.')
                                self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(
                                    tmp_var_object, replace=True)

            shown_var_list = self.return_list_of_shown_variables_in_objectified_element_descendants(
                self.root.page[pagenr])
            for shown_variable in shown_var_list:
                if shown_variable not in self.questionnaire.pages.pages[tmp_pagename].variables.list_all_shown_vars():
                    self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(
                        questionnaire.Variable(varname=shown_variable, vartype='string', varplace='shown'))

                # print(f'## shown: {shown_variable}')

    @staticmethod
    def return_list_of_shown_variables_in_objectified_element_descendants(
            objectified_element: lxml.objectify.ObjectifiedElement) -> list:
        tmp_list_text = [element for element in objectified_element.iterdescendants() if
                         hasattr(element, 'text')]
        tmp_list_with_actual_text = [element for element in tmp_list_text if
                                     element.text is not None]
        tmp_list_with_shown_variables = [element for element in tmp_list_with_actual_text if '.value}' in element.text]

        results_list = []

        for entry in tmp_list_with_shown_variables:
            if isinstance(entry.text, str):
                [results_list.append(found_string) for found_string in
                 re.findall('\{([a-zA-Z0-9_-]+)\.value\}', entry.text) if found_string not in results_list]
        return results_list

    def extract_variables_from_pages_triggers(self):
        self.logger.info("extract_variables_from_pages_triggers")
        for pagenr in range(0, len(self.root.page)):
            tmp_pagename = self.root.page[pagenr].attrib['uid']
            if hasattr(self.root.page[pagenr], 'triggers'):
                for i in self.root.page[pagenr].triggers.iterdescendants():
                    try:
                        tmp_varname = i.attrib['variable']
                        tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(
                            varplace='triggers', varname=tmp_varname)
                        if tmp_varname not in self.questionnaire.pages.pages[
                            tmp_pagename].variables.list_all_vars() and tmp_varname not in \
                                self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                            self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                        else:
                            self.logger.info(
                                'Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(
                                    tmp_pagename) + '". Possible duplicate.')
                            self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(
                                tmp_var_object, replace=True)
                    except KeyError:
                        pass

    def extract_declared_variables(self):
        self.logger.info("extract_declared_variables")
        for i in range(0, len(self.root.variables.variable)):
            # print(self.questionnaire.filename)
            # print(self.root.variables.variable[i].attrib['name'])
            self.questionnaire.variables.add_variable(
                questionnaire.Variable(self.root.variables.variable[i].attrib["name"],
                                       self.root.variables.variable[i].attrib["type"]))

    # def extract_pages_into_tmp_dict(self):
    #     self.logger.info("extract_pages_into_tmp_dict")
    #     for i in range(0, len(self.root.page)):
    #         self.tmp_dict_of_pages[self.root.page[i].attrib['uid']] = self.root.page[i]

    def extract_pages_to_self(self):
        self.logger.info("extract_pages_to_self")
        for i in range(0, len(self.root.page)):
            # get the objectified xml object of the xml page
            tmp_qml_page_source = self.root.page[i]

            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            tmp_qml_page_object = questionnaire.QmlPage(tmp_page_uid, declared=True)

            if tmp_qml_page_source is not None:
                # get the objectified xml, represented as bytes
                tmp_xml_source_bytes = etree.tostring(tmp_qml_page_source)

                # encode bytes to a string
                tmp_xml_source_str_escaped = tmp_xml_source_bytes.decode('utf-8')
                # unescape the html/xml escaped characters
                tmp_xml_source_str = html.unescape(tmp_xml_source_str_escaped)
                # clean the string (of namespace declarations)
                search_string = ' xmlns:zofar="http://www.his.de/zofar/xml/questionnaire" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:display="http://www.dzhw.eu/zofar/xml/display"'
                tmp_xml_source_str = tmp_xml_source_str.replace(search_string, '')
                # add newlines
                tmp_tags_with_newlines_before_list = ['<zofar:transition',
                                                      '<zofar:transitions>',
                                                      '<zofar:body>',
                                                      '<zofar:header>',
                                                      '<zofar:trigger',
                                                      '<zofar:triggers>']
                for entry in tmp_tags_with_newlines_before_list:
                    tmp_xml_source_str = tmp_xml_source_str.replace(entry, '\n\t\t' + entry)

                # save the objectified xml within the QmlPage object
                tmp_qml_page_object.set_xml_source(tmp_qml_page_source)
                # save the unescaped xml string of the page within the QmlPage object
                tmp_qml_page_object.set_xml_source_str(tmp_xml_source_str)
            self.questionnaire.pages.add_page(tmp_qml_page_object)

    def extract_transitions_to_self(self):
        self.logger.info("extract_transitions_to_self")
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            # self.questionnaire.pages.add_page(questionnaire.QmlPage(tmp_page_uid, declared=True))
            self.extract_transitions_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)

    def extract_transitions_from_qml_page_source(self, qml_source_page, uid):
        self.logger.info("extract_transitions_from_qml_page_source from page: " + str(uid))
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

                    source_page_index = self.list_of_pages().index(uid)
                    if tmp_target not in self.list_of_pages():
                        self.questionnaire.pages.add_page(qmlpage=questionnaire.QmlPage(uid=tmp_target, declared=False))
                    target_page_index = self.list_of_pages().index(tmp_target)
                    tmp_distance = target_page_index - source_page_index
                    if 'condition' in tmp_transition_dict:
                        tmp_condition = tmp_transition_dict['condition']
                    else:
                        tmp_condition = None

                    tmp_transition_object = questionnaire.Transition(index=tmp_index,
                                                                     target=tmp_target,
                                                                     condition=tmp_condition,
                                                                     source=uid,
                                                                     distance=tmp_distance)
                    self.questionnaire.pages.pages[uid].transitions.add_transitions(tmp_transition_object)

                    # add transition to sources for each page
                    self.questionnaire.pages.pages[tmp_target].sources.add_source(tmp_transition_object)

    def extract_questions_from_pages(self):
        self.logger.info("extract_questions_from_pages")
        pass

    def extract_headers_and_questions_from_pages(self):
        self.logger.info("extract_headers_from_pages")
        for i in range(0, len(self.root.page)):
            tmp_qml_page_source = self.root.page[i]
            tmp_page_uid = tmp_qml_page_source.attrib['uid']
            self.extract_page_headers_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)
            self.extract_question_objects_from_qml_page_source(tmp_qml_page_source, tmp_page_uid)

    def extract_page_headers_from_qml_page_source(self, qml_source_page, page_uid):
        self.logger.info("extract_page_headers_from_page_sources; uid: " + str(page_uid))
        assert isinstance(qml_source_page, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid, str)
        if hasattr(qml_source_page, 'header'):
            self.logger.info("  found page header")
            i = -1
            if len([i for i in qml_source_page.header.iterchildren()]) > 0:
                self.logger.info("  page header has length > 0")
                for header in qml_source_page.header.iterchildren():
                    tmp_object = None
                    i += 1
                    tmp_index = i
                    self.logger.info("  page header object - index: " + str(i))
                    if 'uid' not in header.attrib:
                        if hasattr(header, 'tag'):
                            if header.tag == 'comment':
                                self.logger.info("  found page header object: xml comment, ignored")
                        else:
                            self.logger.error(
                                '   found object in page header of ' + str(page_uid) + ' that could not be read.')
                        continue
                    tmp_uid = header.attrib['uid']
                    self.logger.info("  page header object - uid: " + str(tmp_uid))
                    if header.text is not None:
                        tmp_text = header.text
                    else:
                        tmp_text = ''
                    self.logger.info("  page header object - text: '" + str(tmp_text) + "'")

                    if 'visible' in header.attrib:
                        tmp_visible_conditions = header.attrib['visible']
                        self.logger.info("  found visible condition: " + str(tmp_visible_conditions))
                    else:
                        tmp_visible_conditions = None
                        self.logger.info("  found visible condition: None")

                    tmp_tag = header.tag[header.tag.rfind('}') + 1:]
                    self.logger.info("  found tag: '" + str(tmp_tag) + "'")
                    tmp_object = questionnaire.PageHeaderObject(uid=tmp_uid, tag=tmp_tag, text=tmp_text,
                                                                index=tmp_index,
                                                                visible_conditions=tmp_visible_conditions)

                    self.logger.info(
                        "  adding PageHeaderObject: '" + str(tmp_object.tag) + "' to page: " + str(page_uid))
                    self.questionnaire.pages.pages[page_uid].header.add_header_object(tmp_object)

            else:
                self.logger.info("  page header has length == 0 and will be ignored")

        else:
            self.logger.info("  no page header found")

    def extract_question_objects_from_qml_page_source(self, qml_source_page, page_uid):
        self.logger.info("extract_question_objects_from_qml_page_source; uid: " + str(page_uid))
        assert isinstance(qml_source_page, lxml.objectify.ObjectifiedElement)
        assert isinstance(page_uid, str)
        if hasattr(qml_source_page, 'body'):
            i = 0
            self.logger.info('  body found on page "' + str(page_uid) + '".')
            if 'uid' in qml_source_page.body.attrib:
                tmp_body_uid = qml_source_page.body.attrib['uid']
            else:
                # ToDo: check if this can be set to None instead of str
                tmp_body_uid = 'None'
            for element in qml_source_page.body.iterchildren():
                tmp_tag = element.tag[element.tag.rfind('}') + 1:]

                if tmp_tag in ['calendar', 'comparison', 'display', 'matrixDouble', 'matrixQuestionMixed',
                               'matrixQuestionOpen', 'matrixQuestionSingleChoice', 'multipleChoice', 'questionOpen',
                               'questionPretest', 'questionSingleChoice']:
                    tmp_index = i
                    i += 1

                if tmp_tag == 'calendar':
                    tmp_question_header_object = self.extract_question_header_from_qml_element_source(element, page_uid)

                elif tmp_tag == 'comparison':
                    pass

                elif tmp_tag == 'display':
                    pass

                elif tmp_tag == 'matrixDouble':
                    pass

                elif tmp_tag == 'matrixMultipleChoice':
                    pass

                elif tmp_tag == 'matrixQuestionMixed':
                    pass

                elif tmp_tag == 'matrixQuestionOpen':
                    pass

                elif tmp_tag == 'matrixQuestionSingleChoice':
                    list_of_items_aos = []
                    list_of_elements = []
                    for entry in element.iterdescendants():
                        if entry.tag[entry.tag.rfind('}') + 1:] == 'item':
                            list_of_elements.append(entry)

                    for item in list_of_elements:
                        list_of_answeroptions = []
                        for item_element in item.iterdescendants():
                            print('444')
                            if item_element.tag[item_element.tag.rfind('}') + 1:] == 'answerOption':
                                tmp_value = None
                                if 'label' in item_element.attrib:
                                    tmp_value = item_element.attrib['label']
                                list_of_answeroptions.append(tmp_value)
                        list_of_items_aos.append(tuple(list_of_answeroptions))

                    if list_of_items_aos:
                        if len(set(list_of_items_aos)) != 1:
                            print(page_uid)
                    print(list_of_items_aos)


                elif tmp_tag == 'multipleChoice':
                    pass

                elif tmp_tag == 'questionOpen':
                    pass

                elif tmp_tag == 'questionPretest':
                    pass

                elif tmp_tag == 'questionSingleChoice':
                    pass

                    # a = self.find_tag_in_descendants(element, 'responseDomain')
                    # b = self.find_attribute_in_descendants(element, 'responseDomain', 'type', 'dropDown')
                    # # ToDo
                    # ## self.questionnaire.pages.pages[page_uid].questions.add_question_object()
                    #
                    # (self.extract_question_header_from_qml_element_source(element, page_uid))
                if tmp_tag == 'section':
                    pass

        pass

    @staticmethod
    def find_tag_in_descendants(objectified_xml_element: lxml.objectify.ObjectifiedElement, tag_str: str) -> bool:
        found_element_bool = False
        y = []
        for entry in objectified_xml_element.iterdescendants():
            if entry.tag[entry.tag.rfind('}') + 1:] == tag_str:
                found_element_bool = True
        return found_element_bool

    @staticmethod
    def find_attribute_in_descendants(objectified_xml_element: lxml.objectify.ObjectifiedElement, tag_str: str,
                                      attribute_str: str, value_str: str) -> bool:
        found_element_bool = False
        y = []
        for entry in objectified_xml_element.iterdescendants():
            if entry.tag[entry.tag.rfind('}') + 1:] == tag_str:
                y.append(entry)

        for entry in y:
            if hasattr(y[0], tag_str) is True:
                if attribute_str in entry.attrib:
                    if entry.attrib[attribute_str] == value_str:
                        found_element_bool = True
        return found_element_bool

    @staticmethod
    def find_question_type_class_to_tag_string(string):
        # tmp_dict = {'calendar': Questionnaire.BodyCalendar, 'comparison': Questionnaire.BodyComparison, 'display':, 'matrixDouble':, 'matrixQuestionMixed':, 'matrixQuestionOpen':, 'matrixQuestionSingleChoice':, 'multipleChoice':, 'questionOpen':, 'questionPretest':, 'questionSingleChoice':}
        return ()

    def extract_response_domains_from_question(self):
        self.logger.info("extract_response_domains_from_question")
        pass

    def extract_items_from_response_domain(self):
        self.logger.info("extract_items_from_response_domain")
        pass

    def extract_answeroptions_from_response_domain(self):
        self.logger.info("extract_answeroptions_from_response_domain")
        pass

    # ToDo: move this method to questionnaire, fix the ToDos below
    def extract_sources_from_questionnaire(self):
        self.logger.info("extract_sources_from_questionnaire")
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
            self.questionnaire.pages.add_page(questionnaire.QmlPage(newpagename, declared=False))
            self.questionnaire.pages.pages[newpagename].sources.add_source(tmp_dict_of_additional_pages[newpagename])

    def extract_triggers_from_pages(self):
        self.logger.info("extract_triggers_from_pages")
        pass

    def extract_question_from_qml_page(self, qml_page):
        self.logger.info("extract_question_from_qml_page")
        assert isinstance(qml_page, lxml.objectify.ObjectifiedElement)

    def extract_triggers_from_qml_page(self, qml_page):
        self.logger.info("extract_triggers_from_qml_page")
        assert isinstance(qml_page, lxml.objectify.ObjectifiedElement)

    # def draw_pgv_graph(self, output_file='output_file.png'):
    #     self.pgv_graph.draw(output_file)

    def extract_question_header_from_qml_element_source(self, qml_source_element, page_uid):
        flag_question = False
        flag_instruction = False
        flag_introduction = False
        tmp_header = questionnaire.QuestionHeader()
        if hasattr(qml_source_element, 'header'):
            for header_question_object in qml_source_element.header.iterchildren():
                j = 0
                if hasattr(header_question_object, 'tag'):
                    if header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'question':
                        self.logger.info('  tag "question" found')
                    elif header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'instruction':
                        self.logger.info('  tag "instruction" found')
                    elif header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'introduction':
                        self.logger.info('  tag "introduction" found')
                    elif header_question_object.tag[header_question_object.tag.rfind('}') + 1:] == 'comment':
                        self.logger.info('  comment found, ignored')
                        continue
                    elif header_question_object.tag == 'comment':
                        self.logger.info('  xml comment found - will be ignored')
                        continue
                    else:
                        self.logger.info('  unexpected tag found: "' + str(
                            header_question_object.tag) + '" in header on page ' + str(page_uid))
                        raise ValueError('  unexpected tag found: "' + str(
                            header_question_object.tag) + '" in header on page ' + str(page_uid))

                tmp_index = j
                j += 1

                tmp_uid = header_question_object.attrib['uid']
                tmp_text = header_question_object.text
                if 'visible' in header_question_object.attrib:
                    tmp_visible = header_question_object.attrib['visible']
                else:
                    tmp_visible = None
                tmp_tag = header_question_object.tag[header_question_object.tag.rfind('}') + 1:]
                tmp_header.add_header_object(
                    questionnaire.QuestionHeaderObject(uid=tmp_uid, text=tmp_text, tag=tmp_tag, index=tmp_index,
                                                       visible_conditions=tmp_visible))
        return tmp_header

        # for header_element in qml_source_element.header:
        #     tmp_uid = header_element.uid
        #     tmp_text = header_element.text
        #     tmp_tag = header.tag[header.tag.rfind('}') + 1:]
        #     tmp_index =
        #     tmp_page_header_object = Questionnaire.PageHeaderObject()
        #     tmp_header.add_header_object()
        pass
