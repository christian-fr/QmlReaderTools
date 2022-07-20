import dataclasses
import html
import os.path
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, NewType, Union, Tuple

import lxml
from lxml import objectify, etree

import logging
from qrt.util import qml
import re
from xml.etree import ElementTree

NS = {'zofar': 'http://www.his.de/zofar/xml/questionnaire'}

ON_EXIT_DEFAULT = 'true'
DIRECTION_DEFAULT = 'forward'
CONDITION_DEFAULT = 'true'


def flatten(ll):
    """
    Flattens given list of lists by one level

    :param ll: list of lists
    :return: flattened list
    """
    return [it for li in ll for it in li]


@dataclass
class Transition:
    target_uid: str
    # condition as spring expression that has to be fulfilled on order to follow the transition
    condition: Optional[str] = None


@dataclass
class Variable:
    name: str
    type: str


TriggerVariable = NewType('TriggerVariable', None)


@dataclass(kw_only=True)
class Trigger:
    condition: Optional[str] = 'true'
    children: Optional[TriggerVariable] = None
    on_exit: Optional[str] = ON_EXIT_DEFAULT
    direction: Optional[str] = DIRECTION_DEFAULT


# noinspection PyDataclass
@dataclass(kw_only=True)
class TriggerRedirect(Trigger):
    target_cond_list: List[Tuple[str, str]]


# noinspection PyDataclass
@dataclass(kw_only=True)
class TriggerVariable(Trigger):
    variable: str
    value: str


# noinspection PyDataclass
@dataclass(kw_only=True)
class TriggerAction(Trigger):
    command: str


# noinspection PyDataclass
@dataclass(kw_only=True)
class TriggerJsCheck(Trigger):
    variable: str
    x_var: str
    y_var: str


@dataclass
class VarRef:
    variable: Variable
    # list of conditions (as spring expression) that have to be fulfilled in order to reach the variable reference
    condition: List[str] = field(default_factory=list)


@dataclass
class EnumValue:
    uid: str
    value: int
    label: str


@dataclass
class EnumValues:
    variable: Variable
    values: List[EnumValue]


@dataclass
class Page:
    uid: str
    transitions: List[Transition]
    var_refs: List[VarRef]
    enum_values: List[EnumValues]


@dataclass
class Questionnaire:
    variables: Dict[str, Variable]
    pages: List[Page]


def transitions(page: ElementTree.Element) -> List[Transition]:
    transitions_list = page.find('./zofar:transitions', NS)
    if transitions_list:
        return [Transition(t.attrib['target'], t.attrib['condition']) if 'condition' in t.attrib else
                Transition(t.attrib['target']) for t in transitions_list]
    return []


RE_VAL = re.compile(r'#\{([a-zA-Z0-9_]+)\.value\}')
RE_VAL_OF = re.compile(r'#\{zofar\.valueOf\(([a-zA-Z0-9_]+)\)\}')
RE_AS_NUM = re.compile(r'#\{zofar\.asNumber\(([a-zA-Z0-9_]+)\)\}')


def extract_var_ref(input: str) -> List[str]:
    # find all strings that match the given regular expressions;
    #  returns list of VARNAMEs for: "#{VARNAME.value}", "#{zofar.valueOf(VARNAME)}", "#{zofar.asNumber(VARNAME)}"
    return RE_VAL.findall(input) + RE_VAL_OF.findall(input) + RE_AS_NUM.findall(input)


def var_refs(page: ElementTree.Element) -> List[str]:
    # get a list of all variables that are used in the texts
    texts = [elmnt.text for elmnt in page.iter() if elmnt.text is not None and len(elmnt.text) > 0]
    return list(set(flatten([extract_var_ref(text) for text in texts])))


def visible_conditions(page: ElementTree.Element) -> List[str]:
    return [element.attrib['visible'] for element in page.iter() if 'visible' in element.attrib]


def zofar_tag(ns: Dict[str, str], ns_name: str, tag_name: str) -> str:
    return f'{{{ns[ns_name]}}}{tag_name}'


def action_trigger(trigger: ElementTree.Element) -> TriggerAction:
    on_exit = None
    direction = None
    condition = CONDITION_DEFAULT
    if 'onExit' in trigger.attrib:
        on_exit = trigger.attrib['onExit']
    if 'direction' in trigger.attrib:
        direction = trigger.attrib['direction']
    if 'condition' in trigger.attrib:
        condition = trigger.attrib['condition']
    if 'command' in trigger.attrib:
        return TriggerAction(command=trigger.attrib['command'],
                             on_exit=on_exit,
                             direction=direction,
                             condition=condition)
    print(ElementTree.tostring(trigger))
    raise KeyError('Key "command" not found for variable trigger.')


def variable_trigger(trigger: ElementTree.Element) -> TriggerVariable:
    if 'variable' in trigger.attrib and 'value' in trigger.attrib:
        condition = CONDITION_DEFAULT
        if 'condition' in trigger.attrib:
            condition = trigger.attrib['condition']
        return TriggerVariable(variable=trigger.attrib['variable'], value=trigger.attrib['value'], condition=condition)
    print(ElementTree.tostring(trigger))
    raise KeyError('Keys "variable" and/or "value" not found for variable trigger.')


def js_check_trigger(trigger: ElementTree.Element) -> TriggerJsCheck:
    if 'variable' in trigger.attrib and 'xvar' in trigger.attrib and 'yvar' in trigger.attrib:
        return TriggerJsCheck(variable=trigger.attrib['variable'], x_var=trigger.attrib['xvar'],
                              y_var=trigger.attrib['yvar'])
    print(ElementTree.tostring(trigger))
    raise KeyError('Keys "variable" and/or "xvar" and/or "yvar" not found for variable trigger.')


def process_trigger(trigger: ElementTree.Element) -> Union[TriggerVariable, TriggerAction, TriggerJsCheck]:
    if trigger.tag == zofar_tag(NS, 'zofar', 'action'):
        return action_trigger(trigger)
    elif trigger.tag == zofar_tag(NS, 'zofar', 'variable'):
        return variable_trigger(trigger)
    elif trigger.tag == zofar_tag(NS, 'zofar', 'jsCheck'):
        return js_check_trigger(trigger)
    else:
        print('XML string:')
        print(ElementTree.tostring(trigger))
        raise NotImplementedError(f'triggers: tag not yet implemented: {trigger.tag}')


def process_triggers(page: ElementTree.Element) -> List[Union[TriggerVariable, TriggerAction, TriggerJsCheck]]:
    # gather all variable triggers
    triggers = page.find('./zofar:triggers', NS)
    if triggers:
        # variable triggers
        trig_list = page.findall('./zofar:triggers/*', NS)
        if trig_list:
            return [process_trigger(trigger) for trigger in trig_list]
    return []


def trig_action_redirect(page: ElementTree.Element) -> List[Transition]:
    # action_trigger()
    x = (page, None, 'false')
    return []


RE_TO_LOAD = re.compile(r"^\s*toLoad\.add\('([0-9a-zA-Z_]+)'\)")
RE_TO_RESET = re.compile(r"^\s*toReset\.add\('([0-9a-zA-Z_]+)'\)")
RE_TO_PERSIST = re.compile(r"^\s*toPersist\.put\('([0-9a-zA-Z_]+)',[a-zA-Z0-9_.]+\)")


def trig_json_vars_reset(page: ElementTree.Element) -> List[str]:
    return flatten([RE_TO_RESET.findall(si.attrib['value']) for si in
                    trig_action_script_items(page=page, direction=None, on_exit='false')])


def trig_json_vars_load(page: ElementTree.Element) -> List[str]:
    return flatten([RE_TO_LOAD.findall(si.attrib['value']) for si in
                    trig_action_script_items(page=page, direction=None, on_exit='false')])


def trig_json_vars_save(page: ElementTree.Element) -> List[str]:
    return flatten([RE_TO_PERSIST.findall(si.attrib['value']) for si in
                    trig_action_script_items(page=page, direction=None, on_exit='true')])


def trig_action_script_items(page: ElementTree.Element,
                             direction: Optional[str],
                             on_exit: Optional[str]) -> List[ElementTree.Element]:
    act_trig = [elmnt for elmnt in page.findall('./zofar:triggers/zofar:action/zofar:scriptItem', NS)]
    return_list = []
    for element in act_trig:
        add_element = True
        if 'onExit' in element.attrib and on_exit is not None:
            if element.attrib['onExit'] != on_exit:
                add_element = False
        if 'direction' in element.attrib and direction is not None:
            if element.attrib['direction'] != direction:
                add_element = False
        if add_element:
            return_list.append(element)
    return return_list


def variables(xml_root: ElementTree.ElementTree):
    # gather all preload variables
    pi_list = flatten([pr.findall('./zofar:preloadItem', NS) for pr in xml_root.find('./zofar:preloads', NS)])
    pl_var_list = [Variable('PRELOAD' + pi.attrib['variable'], 'string') for pi in pi_list]
    # gather all regular variable declarations and add preload variables, return
    return pl_var_list + [Variable(v.attrib['name'], v.attrib['type']) for v in
                          xml_root.find('./zofar:variables', NS).findall('./zofar:variable', NS)]


def redirect_triggers(trig_list: List[Trigger], on_exit: str) -> List[TriggerRedirect]:
    _RE_REDIR_TRIG = re.compile(r"^\s*navigatorBean\.redirect\('([a-zA-Z0-9_]+)'\)\s*$")
    _RE_REDIR_TRIG_AUX = re.compile(r"^\s*navigatorBean\.redirect\(([a-zA-Z0-9_]+)\)\s*$")
    filtered_trig_list = []
    for trigger in trig_list:
        if not isinstance(trigger, TriggerAction):
            continue
        if trigger.on_exit is None and on_exit == ON_EXIT_DEFAULT:
            filtered_trig_list.append(trigger)
        elif trigger.on_exit == on_exit:
            filtered_trig_list.append(trigger)

    helper_vars_list = flatten([_RE_REDIR_TRIG_AUX.findall(trigger.command) for trigger in filtered_trig_list
                                if _RE_REDIR_TRIG_AUX.match(trigger.command) is not None])

    trig_var_val_cond_tuple_list = flatten([[(trig.variable, trig.value, trig.condition) for trig in trig_list if
                                             isinstance(trig, TriggerVariable) and trig.variable == var] for var in
                                            helper_vars_list])

    aux_var_dict = {var_name: [] for var_name in helper_vars_list}
    for var in helper_vars_list:
        for trigger in trig_list:
            if isinstance(trigger, TriggerVariable) and trigger.variable == var:
                aux_var_dict[var].append((trigger.value, trigger.condition))

    return_list = []
    for trigger in filtered_trig_list:
        if not _RE_REDIR_TRIG.match(trigger.command) and \
                not _RE_REDIR_TRIG_AUX.match(trigger.command):
            continue
        if _RE_REDIR_TRIG.match(trigger.command):
            return_list.append(
                TriggerRedirect(target_cond_list=[(_RE_REDIR_TRIG.findall(trigger.command)[0], trigger.condition)],
                                on_exit=trigger.on_exit,
                                direction=trigger.direction))
        elif _RE_REDIR_TRIG_AUX.match(trigger.command):
            aux_var = _RE_REDIR_TRIG_AUX.findall(trigger.command)[0]
            return_list.append(
                TriggerRedirect(target_cond_list=aux_var_dict[aux_var],
                                on_exit=trigger.on_exit,
                                direction=trigger.direction))

    return return_list


def body_vars(page: ElementTree.Element) -> List[str]:
    if page.find('./zofar:body', NS) is not None:
        return [b.attrib['variable'] for b in page.find('./zofar:body', NS).iterfind('.//*[@variable]')]
    return []


@dataclass
class NewPage:
    uid: str
    transitions: List[Transition] = field(default_factory=list)
    var_refs: List[str] = field(default_factory=list)
    _triggers_list: List[Trigger] = field(default_factory=list)
    triggers_vars: List[str] = field(default_factory=list)
    triggers_json_save: List[str] = field(default_factory=list)
    triggers_json_load: List[str] = field(default_factory=list)
    triggers_json_reset: List[str] = field(default_factory=list)
    visible_conditions: List[str] = field(default_factory=list)
    trig_redirect_on_exit_true: List[TriggerRedirect] = field(default_factory=list)
    trig_redirect_on_exit_false: List[TriggerRedirect] = field(default_factory=list)


@dataclass
class NewQuestionnaire:
    pages: List[NewPage] = field(default_factory=list)
    var_declarations: List[Variable] = field(default_factory=list)


def read_xml(xml_path: Path) -> NewQuestionnaire:
    xml_root = ElementTree.parse(xml_path)
    q = NewQuestionnaire()

    q.var_declarations = variables(xml_root)

    for page in xml_root.findall('./zofar:page', NS):
        p = NewPage(page.attrib['uid'])

        p.transitions = transitions(page)
        p.var_ref = var_refs(page)
        p._triggers_list = process_triggers(page)
        p.body_var = body_vars(page)
        p.trig_var = [trig.variable for trig in p._triggers_list if isinstance(trig, TriggerVariable)]
        p.trig_json_save = trig_json_vars_save(page)
        p.trig_json_load = trig_json_vars_load(page)
        p.trig_json_reset = trig_json_vars_reset(page)
        p.visible_conditions = visible_conditions(page)

        p.trig_redirect_on_exit_true = redirect_triggers(p._triggers_list, 'true')
        p.trig_redirect_on_exit_false = redirect_triggers(p._triggers_list, 'false')

        q.pages.append(p)

    return q


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
        self.questionnaire = qml.Questionnaire(file=self.file, title=self.title)

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
                        qml.Variable(varname=shown_variable, vartype='string', varplace='shown'))

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
                qml.Variable(self.root.variables.variable[i].attrib["name"],
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
            tmp_qml_page_object = qml.QmlPage(tmp_page_uid, declared=True)

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
                        self.questionnaire.pages.add_page(qmlpage=qml.QmlPage(uid=tmp_target, declared=False))
                    target_page_index = self.list_of_pages().index(tmp_target)
                    tmp_distance = target_page_index - source_page_index
                    if 'condition' in tmp_transition_dict:
                        tmp_condition = tmp_transition_dict['condition']
                    else:
                        tmp_condition = None

                    tmp_transition_object = qml.Transition(index=tmp_index,
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
            if len([j for j in qml_source_page.header.iterchildren()]) > 0:
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
                    tmp_object = qml.PageHeaderObject(uid=tmp_uid, tag=tmp_tag, text=tmp_text,
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
            self.questionnaire.pages.add_page(qml.QmlPage(newpagename, declared=False))
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
        tmp_header = qml.QuestionHeader()
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
                    qml.QuestionHeaderObject(uid=tmp_uid, text=tmp_text, tag=tmp_tag, index=tmp_index,
                                             visible_conditions=tmp_visible))
        return tmp_header

        # for header_element in qml_source_element.header:
        #     tmp_uid = header_element.uid
        #     tmp_text = header_element.text
        #     tmp_tag = header.tag[header.tag.rfind('}') + 1:]
        #     tmp_index =
        #     tmp_page_header_object = Questionnaire.PageHeaderObject()
        #     tmp_header.add_header_object()file:///home/christian/zofar_workspace/lhc_methodentest/src/main/resources/questionnaire.xml
        pass


if __name__ == '__main__':
    input_xml = Path(os.path.abspath('.'), 'tests', 'context', 'qml', 'questionnaire_lhc.xml')
    questionnaire = read_xml(input_xml)
    pass
