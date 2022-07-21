import os.path
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, NewType, Union, Tuple
import re
from xml.etree import ElementTree

NS = {'zofar': 'http://www.his.de/zofar/xml/questionnaire'}

ON_EXIT_DEFAULT = 'true'
DIRECTION_DEFAULT = 'forward'
CONDITION_DEFAULT = 'true'

RE_VAL = re.compile(r'#{([a-zA-Z0-9_]+)\.value}')
RE_VAL_OF = re.compile(r'#{zofar\.valueOf\(([a-zA-Z0-9_]+)\)}')
RE_AS_NUM = re.compile(r'#{zofar\.asNumber\(([a-zA-Z0-9_]+)\)}')

RE_TO_LOAD = re.compile(r"^\s*toLoad\.add\('([0-9a-zA-Z_]+)'\)")
RE_TO_RESET = re.compile(r"^\s*toReset\.add\('([0-9a-zA-Z_]+)'\)")
RE_TO_PERSIST = re.compile(r"^\s*toPersist\.put\('([0-9a-zA-Z_]+)',[a-zA-Z0-9_.]+\)")

RE_REDIRECT_TRIG = re.compile(r"^\s*navigatorBean\.redirect\('([a-zA-Z0-9_]+)'\)\s*$")
RE_REDIRECT_TRIG_AUX = re.compile(r"^\s*navigatorBean\.redirect\(([a-zA-Z0-9_]+)\)\s*$")


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


# forward declaration of class TriggerVariable
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


def transitions(page: ElementTree.Element) -> List[Transition]:
    transitions_list = page.find('./zofar:transitions', NS)
    if transitions_list:
        return [Transition(t.attrib['target'], t.attrib['condition']) if 'condition' in t.attrib else
                Transition(t.attrib['target']) for t in transitions_list]
    return []


# noinspection SpellCheckingInspection
def extract_var_ref(input_str: str) -> List[str]:
    # find all strings that match the given regular expressions;
    #  returns list of VARNAMEs for: "#{VARNAME.value}", "#{zofar.valueOf(VARNAME)}", "#{zofar.asNumber(VARNAME)}"
    return RE_VAL.findall(input_str) + RE_VAL_OF.findall(input_str) + RE_AS_NUM.findall(input_str)


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


def variables(xml_root: ElementTree.ElementTree) -> Dict[str, Variable]:
    # gather all preload variables
    pi_list = flatten([pr.findall('./zofar:preloadItem', NS) for pr in xml_root.find('./zofar:preloads', NS)])
    pl_var_list = [Variable('PRELOAD' + pi.attrib['variable'], 'string') for pi in pi_list]
    # gather all regular variable declarations and add preload variables, return
    reg_var_list = [Variable(v.attrib['name'], v.attrib['type']) for v in
                    xml_root.find('./zofar:variables', NS).findall('./zofar:variable', NS)]
    return {var.name: var for var in pl_var_list + reg_var_list}


def redirect_triggers(trig_list: List[Trigger], on_exit: str) -> List[TriggerRedirect]:
    filtered_trig_list = []
    for trigger in trig_list:
        if not isinstance(trigger, TriggerAction):
            continue
        if trigger.on_exit is None and on_exit == ON_EXIT_DEFAULT:
            filtered_trig_list.append(trigger)
        elif trigger.on_exit == on_exit:
            filtered_trig_list.append(trigger)

    helper_vars_list = flatten([RE_REDIRECT_TRIG_AUX.findall(trigger.command) for trigger in filtered_trig_list
                                if RE_REDIRECT_TRIG_AUX.match(trigger.command) is not None])

    aux_var_dict = {var_name: [] for var_name in helper_vars_list}
    for var in helper_vars_list:
        for trigger in trig_list:
            if isinstance(trigger, TriggerVariable) and trigger.variable == var:
                aux_var_dict[var].append((trigger.value.strip("'"), trigger.condition))

    return_list = []
    for trigger in filtered_trig_list:
        if not RE_REDIRECT_TRIG.match(trigger.command) and \
                not RE_REDIRECT_TRIG_AUX.match(trigger.command):
            continue
        if RE_REDIRECT_TRIG.match(trigger.command):
            return_list.append(
                TriggerRedirect(target_cond_list=[(RE_REDIRECT_TRIG.findall(trigger.command)[0], trigger.condition)],
                                on_exit=trigger.on_exit,
                                direction=trigger.direction))
        elif RE_REDIRECT_TRIG_AUX.match(trigger.command):
            aux_var = RE_REDIRECT_TRIG_AUX.findall(trigger.command)[0]
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
class Page:
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

    @property
    def triggers_list(self):
        return self._triggers_list


@dataclass
class Questionnaire:
    pages: List[Page] = field(default_factory=list)
    var_declarations: Dict[str, Variable] = field(default_factory=list)


def read_xml(xml_path: Path) -> Questionnaire:
    xml_root = ElementTree.parse(xml_path)
    q = Questionnaire()

    q.var_declarations = variables(xml_root)

    for page in xml_root.findall('./zofar:page', NS):
        p = Page(page.attrib['uid'])

        p.transitions = transitions(page)
        p.var_ref = var_refs(page)
        p._triggers_list = process_triggers(page)
        p.body_var = body_vars(page)
        p.trig_var = [trig.variable for trig in p.triggers_list if isinstance(trig, TriggerVariable)]
        p.trig_json_save = trig_json_vars_save(page)
        p.trig_json_load = trig_json_vars_load(page)
        p.trig_json_reset = trig_json_vars_reset(page)
        p.visible_conditions = visible_conditions(page)

        p.trig_redirect_on_exit_true = redirect_triggers(p.triggers_list, 'true')
        p.trig_redirect_on_exit_false = redirect_triggers(p.triggers_list, 'false')

        q.pages.append(p)

    return q


if __name__ == '__main__':
    input_xml = Path(os.path.abspath('.'), 'tests', 'context', 'qml', 'questionnaire_lhc.xml')
    questionnaire = read_xml(input_xml)
    pass
