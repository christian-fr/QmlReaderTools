class IndexedObject:
    def __init__(self, index_value):
        self.index = index_value

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index_value):
        assert isinstance(index_value, int) or index_value is None
        self.__index = index_value


class UniqueObject(IndexedObject):
    def __init__(self, uid_value, index_value):
        super().__init__(index_value=index_value)
        self.uid = uid_value

    @property
    def uid(self):
        return self.__uid

    @uid.setter
    def uid(self, uid_string):
        assert isinstance(uid_string, str)
        self.__uid = uid_string


class OnPageObjectWithUid(UniqueObject):
    def __init__(self, uid_value, page_uid_value, index_value):
        super().__init__(uid_value=uid_value, index_value=index_value)
        self.page_uid = page_uid_value

    @property
    def page_uid(self):
        return self.__page_uid

    @page_uid.setter
    def page_uid(self, page_uid_value):
        assert isinstance(page_uid_value, str)
        self.__page_uid = page_uid_value


class OnPageObjectWithoutUid(IndexedObject):
    def __init__(self, page_uid_value, index_value):
        super().__init__(index_value=index_value)
        self.page_uid = page_uid_value

    @property
    def page_uid(self):
        return self.__page_uid

    @page_uid.setter
    def page_uid(self, page_uid_value):
        assert isinstance(page_uid_value, str)
        self.__page_uid = page_uid_value


class ConditionObject:
    def __init__(self, condition_string):
        self.condition = condition_string
        self.python_condition = None

    def __str__(self):
        return self.condition

    def evaluate(self):
        if self.python_condition is not None:
            pass
            # Todo: evaluate expression!
            # return True
            # return False
            raise NotImplementedError('Evaluation not yet implemented.')
        else:
            raise NotImplementedError(
                'Condition: "' + str(self.condition) + '" has not yet been translated into python logic!')

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition_string):
        if condition_string is not None:
            assert isinstance(condition_string, str) or isinstance(condition_string, bool)
            self.__condition = condition_string
        else:
            self.__condition = 'true'

    def translate_condition_to_python_logic(self):
        pass


class CanHaveConditionWithUid(OnPageObjectWithUid):
    def __init__(self, uid_value, page_uid_value, index_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value)
        self.condition = ConditionObject(condition_string=condition_string)

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition_object):
        assert isinstance(condition_object, ConditionObject)
        self.__condition = condition_object


class CanHaveConditionWithoutUid(OnPageObjectWithoutUid):
    def __init__(self, page_uid_value, index_value, condition_string='True'):
        super().__init__(page_uid_value=page_uid_value, index_value=index_value)
        self.condition = ConditionObject(condition_string=condition_string)

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition_object):
        assert isinstance(condition_object, ConditionObject)
        self.__condition = condition_object


class VariableObject:
    def __init__(self, name_string, var_type_string):
        self._allowed_var_types = ['string', 'boolean', 'singleChoiceAnswerOption', 'number']
        self.name = name_string
        self.var_type = var_type_string
        self.var_value = None
        self.var_page_list = []

    def __str__(self):
        return self.name, self.var_type

    def get_var_page_list(self):
        return self.var_page_list

    def add_var_page_list(self, page_uid):
        assert isinstance(page_uid, str)
        if page_uid not in self.var_page_list:
            self.var_page_list.append(page_uid)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name_string):
        assert isinstance(name_string, str)
        self.__name = name_string

    @property
    def var_type(self):
        return self.__type

    @var_type.setter
    def var_type(self, var_type_string):
        assert isinstance(var_type_string, str) and var_type_string in self._allowed_var_types
        self.__type = var_type_string

    @property
    def var_value(self):
        return self.__var_value

    @var_value.setter
    def var_value(self, value):
        assert isinstance(value, str) or isinstance(value, int) or value is None
        self.__var_value = value


class VariableSimulation:
    def __init__(self):
        self.dict_of_variables = {}

    def add_variable(self, variable_object):
        assert isinstance(variable_object, VariableObject)
        if variable_object.name in self.dict_of_variables:
            raise KeyError('Variable with name "' + variable_object.name + '" already added!')
        else:
            self.dict_of_variables[variable_object.name] = variable_object

    def get_variable_by_name(self, var_name):
        assert isinstance(var_name, str)
        if var_name in self.dict_of_variables.keys():
            return self.dict_of_variables[var_name]
        else:
            raise KeyError('Variable name: "' + var_name + '" not found.')

    def set_variable_by_name(self, var_name, value):
        assert isinstance(var_name, str)
        if var_name in self.dict_of_variables.keys():
            self.dict_of_variables[var_name].set_value(value)


class PageObject(UniqueObject):
    def __init__(self, uid_value, index_value, declared=True):
        super().__init__(uid_value=uid_value, index_value=index_value)

        self.declared = declared

        self.page_headers_dict = {}
        self.sources_dict = {}
        self.transitions_dict = {}
        self.triggers_dict = {}
        self.page_body_objects_dict = {}

    @property
    def declared(self):
        return self._declared

    @declared.setter
    def declared(self, declared_bool):
        assert isinstance(declared_bool, bool)
        self._declared = declared_bool

    def get_all_var_names_list(self):
        # ToDo: yet to be implemented
        raise NotImplementedError()

    def get_all_duplicate_var_names_list(self):
        # ToDo: yet to be implemented
        raise NotImplementedError()

    def get_all_sources_list(self):
        return list(self.sources_dict.keys())

    def get_all_transitions_list(self):
        return ['source: {0}, index: {1}, target: {2}, condition: "{3}"'.format(val.page_uid, str(val.index),
                                                                                val.target_page_uid,
                                                                                str(val.condition.condition)) for val in
                self.transitions_dict.values()]

    def get_all_triggers_list(self):
        # ToDo: display var_names of variable trigger
        return list(self.triggers_dict.keys())

    def get_all_questions_list(self):
        return list(self.page_body_objects_dict.keys())

    def get_question_from_index(self, index):
        return self.page_body_objects_dict[index]

    def add_source(self, source_object):
        assert isinstance(source_object, SourceObject)
        if source_object.index not in self.sources_dict.keys():
            self.sources_dict[source_object.index] = source_object
        else:
            raise KeyError('Source with index="' + str(
                source_object.index) + '" already present in sources_dict of page="' + self.uid + '"')

    def add_transition(self, transition_object):
        assert isinstance(transition_object, TransitionObject)
        if transition_object.index not in self.transitions_dict.keys():
            self.transitions_dict[transition_object.index] = transition_object
        else:
            raise KeyError('Transition with index="' + str(
                transition_object.index) + '" already present in transitions_dict on page="' + self.uid + '"')

    def add_trigger(self, trigger_object):
        assert isinstance(trigger_object, TriggerObject)
        if trigger_object.index not in self.triggers_dict.keys():
            self.triggers_dict[trigger_object.index] = trigger_object
        else:
            raise KeyError('Transition with index="' + str(
                trigger_object.index) + '" already present in triggers_dict on page="' + self.uid + '"')

    def add_page_header_object(self, page_header_object):
        assert isinstance(page_header_object, PageHeaderObject)
        if page_header_object.index not in self.page_headers_dict.keys():
            self.page_headers_dict[page_header_object.index] = page_header_object
        else:
            raise KeyError('Page header with index="' + str(
                page_header_object.index) + '" already present in page_headers_dict on page="' + self.uid + '"')

    def add_page_body_object(self, question_or_section_object):
        assert isinstance(question_or_section_object, QuestionObjectClass) or isinstance(question_or_section_object,
                                                                                         PageHeaderObject)
        if question_or_section_object.index not in self.page_body_objects_dict.keys():
            self.page_body_objects_dict[question_or_section_object.index] = question_or_section_object
            tmp_unique_uids_list = []
            for question_or_section_object in self.page_body_objects_dict.values():
                if question_or_section_object.uid not in tmp_unique_uids_list:
                    tmp_unique_uids_list.append(question_or_section_object.uid)
                else:
                    print('Duplicate uid="{0}" found on page="{1}"'.format(question_or_section_object.uid, self.uid))
        else:
            raise KeyError(
                'Question with index="{0}", uid="{1}" already present in self.questions_dict on page="{2}"'.format(
                    str(question_or_section_object.index), question_or_section_object.uid, self.uid))

    def get_page_object_max_index(self):
        tmp_max_page_headers_index = None
        tmp_max_questions_index = None

        if list(self.page_headers_dict.keys()):
            tmp_max_page_headers_index = max(list(self.page_headers_dict.keys()))

        if list(self.page_body_objects_dict.keys()):
            tmp_max_questions_index = max(list(self.page_body_objects_dict.keys()))
        if tmp_max_questions_index is None:
            if tmp_max_page_headers_index is None:
                return None
            else:
                return tmp_max_page_headers_index
        else:
            if tmp_max_page_headers_index is None:
                return tmp_max_questions_index
            else:
                return max([tmp_max_page_headers_index, tmp_max_questions_index])

    def get_page_object_next_index(self):
        tmp_max_index = self.get_page_object_max_index()
        if tmp_max_index is None:
            return 0
        else:
            tmp_max_index += 1
            return tmp_max_index


class TransitionObject(CanHaveConditionWithoutUid):
    def __init__(self, page_uid_value, target_page_uid_value, index_value, condition_string='True'):
        super().__init__(page_uid_value=page_uid_value, condition_string=condition_string, index_value=index_value)
        self.target_page_uid = target_page_uid_value

    @property
    def target_page_uid(self):
        return self.__target_page_uid

    @target_page_uid.setter
    def target_page_uid(self, target_page_uid_value):
        assert isinstance(target_page_uid_value, str)
        self.__target_page_uid = target_page_uid_value


class SourceObject(CanHaveConditionWithUid):
    def __init__(self, page_uid_value, source_page_uid_value, index_value, condition_string='True'):
        super().__init__(uid_value=None, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        # ToDo: finish writing this class with @property getters / setters
        self.source_page_uid = source_page_uid_value
        self.page_uid = page_uid_value
        self.condition = condition_string

    @property
    def source_page_uid(self):
        return self.__source_page_uid

    @source_page_uid.setter
    def source_page_uid(self, source_page_uid_string):
        assert isinstance(source_page_uid_string, str)
        self.__source_page_uid = source_page_uid_string


class TriggerObject(CanHaveConditionWithUid):
    def __init__(self, page_uid_value, index_value, var_name_string, value_string, condition_string='True'):
        # ToDo: finish writing this class with @property getters / setters
        super().__init__(uid_value=None, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        self.condition = condition_string
        self.var_name = var_name_string
        self.value = value_string

    def translate_value_to_python_logic(self):
        # ToDo: yet to be implemented
        pass


class Pages:
    def __init__(self, questionnaire_uid_value):
        self.pages_dict = {}
        self.questionnaire_uid = questionnaire_uid_value

    @property
    def questionnaire_uid(self):
        return self.__questionnaire_uid

    @questionnaire_uid.setter
    def questionnaire_uid(self, questionnaire_uid_value):
        assert isinstance(questionnaire_uid_value, str)
        self.__questionnaire_uid = questionnaire_uid_value

    def get_all_pages_list(self):
        return list(self.pages_dict.keys())

    def get_page_by_uid(self, uid):
        assert isinstance(uid, str)
        if uid in self.pages_dict.keys():
            return self.pages_dict[uid]
        else:
            print('Page "' + str(uid) + '" not found.')

    def add_page(self, page_object):
        assert isinstance(page_object, PageObject)
        if page_object.uid not in self.pages_dict.keys():
            self.pages_dict[page_object.uid] = page_object
        else:
            raise KeyError('Page with uid="" already present in pages_dict.')


class HeaderObject(CanHaveConditionWithUid):
    def __init__(self, uid_value, page_uid_value, header_text_string, index_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        self.allowed_header_types = ['None']
        self.text = header_text_string

    @property
    def allowed_header_types(self):
        return self.__allowed_header_types

    @allowed_header_types.setter
    def allowed_header_types(self, allowed_header_types_list):
        assert isinstance(allowed_header_types_list, list)
        for entry in allowed_header_types_list:
            assert isinstance(entry, str)
        self.__allowed_header_types = allowed_header_types_list

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, header_text_string):
        assert isinstance(header_text_string, str) or header_text_string is None
        self.__text = header_text_string


class QuestionHeaderBaseObject(HeaderObject):
    def __init__(self, uid_value, page_uid_value, header_text_string, index_value,
                 condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         header_text_string=header_text_string, index_value=index_value)


class ResponseDomainHeaderObject(QuestionHeaderBaseObject):
    def __init__(self, uid_value, page_uid_value, header_type_string, header_text_string, index_value,
                 condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         header_text_string=header_text_string, index_value=index_value)
        self.__allowed_header_types_list = ['title']
        self.header_type = header_type_string
        self.text = header_text_string

    def __str__(self):
        return 'header type = "{0}", uid = "{1}", page_uid = "{2}", index = "{3}"'.format(self.header_type, self.uid,
                                                                                          self.page_uid,
                                                                                          str(self.index))

    @property
    def header_type(self):
        return self.__header_type

    @header_type.setter
    def header_type(self, header_type_string):
        try:
            assert isinstance(header_type_string, str) and header_type_string in self.__allowed_header_types_list
        except AssertionError:
            raise TypeError(
                'Object with uid="{0}" is of header_type="{1}", not of allowed_header_types: "{2}", page "{3}"'.format(
                    self.uid, header_type_string, str(self.__allowed_header_types_list), self.page_uid))
        self.__header_type = header_type_string


class QuestionHeaderObject(QuestionHeaderBaseObject):
    def __init__(self, uid_value, page_uid_value, header_type_string, header_text_string, index_value,
                 condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         header_text_string=header_text_string, index_value=index_value)
        self.__allowed_header_types_list = ['question', 'instruction', 'introduction']
        self.header_type = header_type_string
        self.text = header_text_string

    def __str__(self):
        return 'header type = "{0}", uid = "{1}", page_uid = "{2}", index = "{3}"'.format(self.header_type, self.uid,
                                                                                          self.page_uid,
                                                                                          str(self.index))

    @property
    def header_type(self):
        return self.__header_type

    @header_type.setter
    def header_type(self, header_type_string):
        try:
            assert isinstance(header_type_string, str) and header_type_string in self.__allowed_header_types_list
        except AssertionError:
            raise TypeError(
                'Object with uid="{0}" is of header_type="{1}", not of allowed_header_types: "{2}", page "{3}"'.format(
                    self.uid, header_type_string, str(self.__allowed_header_types_list), self.page_uid))
        self.__header_type = header_type_string


class PageHeaderObject(HeaderObject):
    def __init__(self, uid_value, page_uid_value, page_header_type_string, page_header_text_string, index_value,
                 condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         header_text_string=page_header_text_string, index_value=index_value)
        self.allowed_header_types_list = ['title', 'text', 'instruction']
        self.dict_of_page_headers = {}
        self.page_header_type = page_header_type_string

    @property
    def page_header_type(self):
        return self.__page_header_type

    @page_header_type.setter
    def page_header_type(self, page_header_type_string):
        try:
            assert isinstance(page_header_type_string,
                              str) and page_header_type_string in self.allowed_header_types_list
        except AssertionError:
            raise TypeError(
                'Object with uid="{0}" is of header_type="{1}", not of allowed_header_types: "{2}"'.format(self.uid,
                                                                                                           page_header_type_string,
                                                                                                           str(
                                                                                                               self.allowed_header_types_list)))
        self.__page_header_type = page_header_type_string


class AnswerOptionObject(CanHaveConditionWithUid):
    def __init__(self, uid_value, question_uid_value, page_uid_value, var_name_string, index_value, response_domain_uid,
                 label_text_value=None, missing_bool=False, ao_value=None, condition_string='True',
                 unit_object=None, attached_open=None, variable_name_string=None, exclusive_bool=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        self.label_text = label_text_value
        self.var_name = var_name_string
        self.response_domain_uid = response_domain_uid
        self.missing_flag = missing_bool
        self.value = ao_value
        self.question_uid = question_uid_value
        self.unit_object = unit_object
        self.attached_open = attached_open
        self.variable = variable_name_string
        self.exclusive_flag = exclusive_bool

    @property
    def variable(self):
        return self._variable

    @variable.setter
    def variable(self, variable_name_string_value):
        assert isinstance(variable_name_string_value, str) or variable_name_string_value is None
        self._variable = variable_name_string_value

    @property
    def attached_open(self):
        return self._attached_open

    @attached_open.setter
    def attached_open(self, question_open_object):
        assert isinstance(question_open_object, QuestionOpen) or question_open_object is None
        self._attached_open = question_open_object

    @property
    def unit_object(self):
        return self._belongs_to_unit_uid

    @unit_object.setter
    def unit_object(self, belongs_to_unit_object):
        assert isinstance(belongs_to_unit_object, UnitObject) or belongs_to_unit_object is None
        self._belongs_to_unit_uid = belongs_to_unit_object

    def __str__(self):
        return str((self.page_uid, str(self.index), self.uid, self.label_text, str(self.value), str(self.missing_flag),
                    str(self.condition)))

    @property
    def question_uid(self):
        return self._question_uid

    @question_uid.setter
    def question_uid(self, question_uid_string):
        assert isinstance(question_uid_string, str)
        self._question_uid = question_uid_string

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, ao_value):
        assert isinstance(ao_value, int) or ao_value is None
        self._value = ao_value

    @property
    def missing_flag(self):
        return self._missing_flag

    @missing_flag.setter
    def missing_flag(self, missing_bool):
        assert isinstance(missing_bool, bool) or missing_bool is None
        self._missing_flag = missing_bool

    @property
    def exclusive_flag(self):
        return self._exclusive_flag

    @exclusive_flag.setter
    def exclusive_flag(self, exclusive_bool):
        assert isinstance(exclusive_bool, bool) or exclusive_bool is None
        self._exclusive_flag = exclusive_bool

    @property
    def response_domain_uid(self):
        return self._response_domain_uid

    @response_domain_uid.setter
    def response_domain_uid(self, response_domain_uid_value):
        assert isinstance(response_domain_uid_value, str)
        self._response_domain_uid = response_domain_uid_value

    @property
    def var_name(self):
        return self._var_name

    @var_name.setter
    def var_name(self, var_name_string):
        assert isinstance(var_name_string, str)
        self._var_name = var_name_string

    @property
    def label_text(self):
        return self._label_text

    @label_text.setter
    def label_text(self, label_text_value):
        assert isinstance(label_text_value, str) or label_text_value is None
        self._label_text = label_text_value


class PageBody(UniqueObject):
    def __init__(self, uid_value):
        super().__init__(uid_value=uid_value, index_value=0)


class QuestionObjectBaseClass(CanHaveConditionWithUid):
    def __init__(self, uid_value, page_uid_value, index_value, condition_string='True', list_of_units=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value,
                         condition_string=condition_string)
        self.variables_dict = {}
        self.question_header_dict = {}
        self.answer_option_dict = {}
        self.list_of_unit_objects = []
        self.add_list_of_units(list_of_units)

    def add_list_of_units(self, list_of_unit_objects):
        assert isinstance(list_of_unit_objects, list) or list_of_unit_objects is None
        if list_of_unit_objects is not None:
            for unit_object in list_of_unit_objects:
                assert isinstance(unit_object, UnitObject)
                self.list_of_unit_objects.append(UnitObject)

    def add_question_header(self, question_header_object):
        assert isinstance(question_header_object, QuestionHeaderObject)
        if question_header_object.index not in self.question_header_dict.keys():
            self.question_header_dict[question_header_object.index] = question_header_object
        else:
            raise KeyError('QuestionHeaderObject with index="' + str(
                question_header_object.index) + '" already in question_header_dict of question with uid="' + self.uid + '" on page="' + self.page_uid + '"')

    def get_all_variables_list(self):
        return list(self.variables_dict.keys())

    def get_variable_object_from_var_name(self, var_name_string):
        assert isinstance(var_name_string, str) and var_name_string in self.variables_dict.keys()
        return self.variables_dict[var_name_string]

    def add_variable(self, variable_object):
        assert isinstance(variable_object, VariableObject)
        if variable_object.name not in self.variables_dict.keys():
            self.variables_dict[variable_object.name] = variable_object
        else:
            print('Variable "' + variable_object.name + '" already found in Question.variables_dict!')

    def add_answer_option(self, answer_option_object):
        assert isinstance(answer_option_object, AnswerOptionObject)
        if answer_option_object.uid not in self.answer_option_dict.keys():
            self.answer_option_dict[answer_option_object.uid] = answer_option_object
        else:
            raise KeyError(
                'AnswerOptionObject with uid="{0}" already present in self.answer_option_dict for question with uid="{1}" on page_uid="{2}"'.format(
                    answer_option_object.uid, self.uid, self.page_uid))

    def get_question_header_object_max_index(self):
        tmp_max_question_headers_index = None

        if list(self.question_header_dict.keys()):
            tmp_max_question_headers_index = max(list(self.question_header_dict.keys()))
        if tmp_max_question_headers_index is not None:
            return tmp_max_question_headers_index
        else:
            return None

    def get_question_header_object_next_index(self):
        tmp_max_index = self.get_question_header_object_max_index()
        if tmp_max_index is None:
            return 0
        else:
            tmp_max_index += 1
            return tmp_max_index


class QuestionObjectClass(QuestionObjectBaseClass):
    def __init__(self, uid_value, page_uid_value, index_value, question_header_objects_list, condition_string='True',
                 list_of_units=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value, list_of_units=list_of_units)
        self.item_dict = {}
        self.add_question_header_objects_list(question_header_objects_list)

    def add_item(self, item_object):
        assert isinstance(item_object, MatrixQuestionSingleChoiceItemObject)
        if item_object.uid not in self.item_dict.keys():
            self.item_dict[item_object.uid] = item_object
        else:
            raise KeyError(
                'Item with uid="' + item_object.uid + '" already present in question with uid="' + self.uid + '" on page="' + self.page_uid + '"')

    def add_question_header_objects_list(self, question_header_objects_list):
        assert isinstance(question_header_objects_list, list)
        for question_header_object in question_header_objects_list:
            assert isinstance(question_header_object, QuestionHeaderObject)
            self.add_question_header(question_header_object=question_header_object)


class QuestionMultipleChoiceObject(QuestionObjectClass):
    def __init__(self, uid_value, page_uid_value, index_value, answer_option_objects_list,
                 question_header_objects_list=None, condition_string='True', list_of_units=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value, question_header_objects_list=question_header_objects_list,
                         list_of_units=list_of_units)
        self.variables_list = []
        self.add_answer_option_objects_list(answer_option_objects_list)

    def add_answer_option_objects_list(self, answer_option_objects_list):
        assert isinstance(answer_option_objects_list, list)
        for answer_option_object in answer_option_objects_list:
            assert isinstance(answer_option_object, AnswerOptionObject)
        for answer_option_object in answer_option_objects_list:
            self.add_answer_option(answer_option_object=answer_option_object)


class QuestionSingleChoiceObject(QuestionObjectClass):
    def __init__(self, uid_value, page_uid_value, index_value, answer_option_objects_list,
                 question_header_objects_list=None, condition_string='True', list_of_units=None,
                 response_domain_type_value=None, outer_uid_value=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value, question_header_objects_list=question_header_objects_list,
                         list_of_units=list_of_units)
        self.__allowed_response_domain_types_list = ['dropdown', 'radio']
        self.variables_list = []
        self.add_answer_option_objects_list(answer_option_objects_list)
        self.response_domain_type = response_domain_type_value
        self.outer_uid = outer_uid_value

    @property
    def outer_uid(self):
        return self._outer_uid

    @outer_uid.setter
    def outer_uid(self, outer_uid_value):
        assert isinstance(outer_uid_value, str) or outer_uid_value is None
        self._outer_uid = outer_uid_value

    @property
    def response_domain_type(self):
        return self._response_domain_type

    @response_domain_type.setter
    def response_domain_type(self, response_domain_type_value):
        assert (isinstance(response_domain_type_value,
                           str) and response_domain_type_value in self.__allowed_response_domain_types_list) or response_domain_type_value is None
        self._response_domain_type = response_domain_type_value

    def add_answer_option_objects_list(self, answer_option_objects_list):
        assert isinstance(answer_option_objects_list, list)
        for answer_option_object in answer_option_objects_list:
            assert isinstance(answer_option_object, AnswerOptionObject)
        for answer_option_object in answer_option_objects_list:
            self.add_answer_option(answer_option_object=answer_option_object)


class MatrixQuestionSingleChoiceItemObject(QuestionSingleChoiceObject):
    def __init__(self, uid_value, page_uid_value, index_value, answer_option_objects_list, question_header_objects_list,
                 condition_string='True', list_of_units=None, is_show_values_bool=None, no_response_options_value=None):
        super().__init__(uid_value=uid_value,
                         page_uid_value=page_uid_value,
                         condition_string=condition_string,
                         index_value=index_value,
                         answer_option_objects_list=answer_option_objects_list,
                         question_header_objects_list=question_header_objects_list,
                         list_of_units=list_of_units)

        self.is_show_values_flag = is_show_values_bool
        self.no_response_options = no_response_options_value

    @property
    def no_response_options(self):
        return self._no_response_options

    @no_response_options.setter
    def no_response_options(self, no_response_options_value):
        assert isinstance(no_response_options_value, str) or isinstance(no_response_options_value,
                                                                        int) or no_response_options_value is None
        if isinstance(no_response_options_value, str):
            self._no_response_options = int(no_response_options_value)
        elif isinstance(no_response_options_value, int):
            self._no_response_options = no_response_options_value
        elif no_response_options_value is None:
            self._no_response_options = None

    @property
    def is_show_values_flag(self):
        return self._is_show_values_flag

    @is_show_values_flag.setter
    def is_show_values_flag(self, is_show_values_bool):
        assert isinstance(is_show_values_bool, bool) or is_show_values_bool is None
        if is_show_values_bool:
            self._is_show_values_flag = True
        elif is_show_values_bool is False:
            self._is_show_values_flag = False
        elif is_show_values_bool is None:
            self._is_show_values_flag = None


class PrefixPostfixLabelBaseObject(CanHaveConditionWithUid):
    def __init__(self, uid, page_uid_value, index_value, label_text_value=None, condition_string='True'):
        super().__init__(uid_value=uid, page_uid_value=page_uid_value, index_value=index_value,
                         condition_string=condition_string)
        self.label = label_text_value

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, label_value):
        assert isinstance(label_value, str) or label_value is None
        self.__label = label_value


class PrefixLabelObject(PrefixPostfixLabelBaseObject):
    def __init__(self, uid, page_uid_value, index_value, label_text_value, condition_string='True'):
        super().__init__(uid=uid, page_uid_value=page_uid_value, label_text_value=label_text_value,
                         condition_string=condition_string, index_value=index_value)


class PostfixLabelObject(PrefixPostfixLabelBaseObject):
    def __init__(self, uid, page_uid_value, index_value, label_text_value, condition_string='True'):
        super().__init__(uid=uid, page_uid_value=page_uid_value, label_text_value=label_text_value,
                         condition_string=condition_string, index_value=index_value)


class QuestionOpen(QuestionObjectClass):
    def __init__(self, uid_value, page_uid_value, index_value, var_name_string, condition_string='True',
                 small_option='False', rows=None, columns=None, max_value=None, min_value=None, max_length=None,
                 question_open_type='text', validation_message=None, size=None, prefix_label_object_list=None,
                 postfix_label_object_list=None, question_header_objects_list=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value,
                         condition_string=condition_string, question_header_objects_list=question_header_objects_list)
        self._allowed_question_types = ['text', 'grade', 'number']
        self.var_name = var_name_string
        self.small_option = small_option
        self.rows = rows
        self.columns = columns
        self.max_value = max_value
        self.min_value = min_value
        self.max_length = max_length
        self.question_open_type = question_open_type
        self.validation_message = validation_message
        self.size = size

        self.prefix_label_list = []
        self.add_prefix_label(prefix_label_object_list)

        self.postfix_label_list = []
        self.add_postfix_label(postfix_label_object_list)

    def add_prefix_label(self, prefix_label_object_list):
        assert isinstance(prefix_label_object_list, list)
        for label_object in prefix_label_object_list:
            assert isinstance(label_object, PrefixLabelObject) or label_object is None
            if label_object is not None:
                self.prefix_label_list.append(label_object)

    def add_postfix_label(self, postfix_label_object_list):
        assert isinstance(postfix_label_object_list, list)
        for label_object in postfix_label_object_list:
            assert isinstance(label_object, PostfixLabelObject) or label_object is None
            if label_object is not None:
                self.postfix_label_list.append(label_object)

    @property
    def max_value(self):
        return self._max_value

    @max_value.setter
    def max_value(self, max_value_value):
        assert isinstance(max_value_value, int) or isinstance(max_value_value, str) or max_value_value is None
        if isinstance(max_value_value, int) or max_value_value is None:
            self._max_value = max_value_value
        elif isinstance(max_value_value, str):
            self._max_value = int(max_value_value)
        else:
            raise ValueError(
                'Value "{0}" not recognized for attribute "max_value", question_uid = "{1}", page_uid = "{2}"'.format(
                    str(max_value_value), self.uid, self.page_uid))

    @property
    def min_value(self):
        return self._min_value

    @min_value.setter
    def min_value(self, min_value_value):
        assert isinstance(min_value_value, int) or isinstance(min_value_value, str) or min_value_value is None
        if isinstance(min_value_value, int) or min_value_value is None:
            self._min_value = min_value_value
        elif isinstance(min_value_value, str):
            self._min_value = int(min_value_value)
        else:
            raise ValueError(
                'Value "{0}" not recognized for attribute "min_value", question_uid = "{1}", page_uid = "{2}"'.format(
                    str(min_value_value), self.uid, self.page_uid))

    @property
    def max_length(self):
        return self._max_length

    @max_length.setter
    def max_length(self, max_length_value):
        assert isinstance(max_length_value, int) or isinstance(max_length_value, str) or max_length_value is None
        if isinstance(max_length_value, int) or max_length_value is None:
            self._max_length = max_length_value
        elif isinstance(max_length_value, str):
            self._max_length = int(max_length_value)
        else:
            raise ValueError(
                'Value "{0}" not recognized for attribute "max_length", question_uid = "{1}", page_uid = "{2}"'.format(
                    str(max_length_value), self.uid, self.page_uid))

    @property
    def question_open_type(self):
        return self._question_open_type

    @question_open_type.setter
    def question_open_type(self, question_open_types_value):
        assert isinstance(question_open_types_value, str) or question_open_types_value is None
        if question_open_types_value not in self._allowed_question_types and question_open_types_value is not None:
            raise TypeError('Question type "{0}" was not found in allowed list of types: "{1}".'.format(
                str(question_open_types_value), str(self._allowed_question_types)))
        self._question_open_type = question_open_types_value

    @property
    def validation_message(self):
        return self._validation_message

    @validation_message.setter
    def validation_message(self, validation_messages_value):
        assert isinstance(validation_messages_value, str) or validation_messages_value is None
        self._validation_message = validation_messages_value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size_value):
        assert isinstance(size_value, int) or isinstance(size_value, str) or size_value is None
        if isinstance(size_value, int) or size_value is None:
            self._size = size_value
        elif isinstance(size_value, str):
            self._size = int(size_value)
        else:
            raise ValueError(
                'Value "{0}" not recognized for attribute "size", question_uid = "{1}", page_uid = "{2}"'.format(
                    str(size_value), self.uid, self.page_uid))

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, columns_value):
        assert isinstance(columns_value, int) or isinstance(columns_value, str) or columns_value is None
        if isinstance(columns_value, int) or columns_value is None:
            self._columns = columns_value
        elif isinstance(columns_value, str):
            self._columns = int(columns_value)
        else:
            raise ValueError(
                'Value "{0}" not recognized for attribute "columns", question_uid = "{1}", page_uid = "{2}"'.format(
                    str(columns_value), self.uid, self.page_uid))

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, rows_value):
        assert isinstance(rows_value, int) or isinstance(rows_value, str) or rows_value is None
        if isinstance(rows_value, int) or rows_value is None:
            self._rows = rows_value
        elif isinstance(rows_value, str):
            self._rows = int(rows_value)
        else:
            raise ValueError(
                'Value "{0}" not recognized for attribute "rows", question_uid = "{1}", page_uid = "{2}"'.format(
                    str(rows_value), self.uid, self.page_uid))

    @property
    def small_option(self):
        return self._small_option

    @small_option.setter
    def small_option(self, small_option_value):
        assert isinstance(small_option_value, str) or isinstance(small_option_value, bool) or small_option_value is None
        if isinstance(small_option_value, str):
            if small_option_value is None:
                self._small_option = None
            elif small_option_value.lower() == "true":
                self._small_option = True
            elif small_option_value.lower() == "false":
                self._small_option = False
            else:
                raise ValueError(
                    'Value "{0}" not recognized for attribute "smallOption", question_uid = "{1}", page_uid = "{2}"'.format(
                        str(small_option_value), self.uid, self.page_uid))
        elif isinstance(small_option_value, bool) or small_option_value is None:
            self._small_option = small_option_value

    @property
    def var_name(self):
        return self._var_name

    @var_name.setter
    def var_name(self, var_name_string):
        assert isinstance(var_name_string, str)
        self._var_name = var_name_string


class QuestionMatrixQuestionSingleChoiceObject(QuestionObjectClass):
    def __init__(self, uid_value, page_uid_value, index_value, mqsc_response_domain_header_objects_list,
                 condition_string='True', mqsc_item_objects_list=None, question_header_objects_list=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value,
                         condition_string=condition_string, question_header_objects_list=question_header_objects_list)

        self.items_dict = {}
        self.add_mqsc_items_list(mqsc_item_objects_list)
        self.response_domain_headers_dict = {}
        self.add_mqsc_response_domain_header_objects_list(mqsc_response_domain_header_objects_list)

    def add_mqsc_items_list(self, mqsc_item_objects_list):
        assert isinstance(mqsc_item_objects_list, list)
        for mqsc_item_object in mqsc_item_objects_list:
            assert isinstance(mqsc_item_object, QuestionSingleChoiceObject)
            if mqsc_item_object.uid not in self.items_dict.keys():
                self.items_dict[mqsc_item_object.uid] = mqsc_item_object
            else:
                raise KeyError(
                    'MatrixQuestionSingleChoiceItemObject with uid="{0}" already present in self.items_dict for question with uid="{1}" on page_uid="{2}"'.format(
                        mqsc_item_object.uid, self.uid, self.page_uid))

    def add_mqsc_response_domain_header_objects_list(self, mqsc_response_domain_header_objects_list):
        assert isinstance(mqsc_response_domain_header_objects_list, list)
        for mqsc_response_domain_header_object in mqsc_response_domain_header_objects_list:
            assert isinstance(mqsc_response_domain_header_object, ResponseDomainHeaderObject)
            if mqsc_response_domain_header_object.uid not in self.response_domain_headers_dict.keys():
                self.response_domain_headers_dict[
                    mqsc_response_domain_header_object.uid] = mqsc_response_domain_header_object
            else:
                raise KeyError(
                    'ResponseDomainHeaderObject with uid="{0}" already present in self.items_dict for question with uid="{1}" on page_uid="{2}"'.format(
                        mqsc_response_domain_header_object.uid, self.uid, self.page_uid))


class Section(CanHaveConditionWithUid):
    def __init__(self, uid_value, index_value, page_uid_value, condition_string):
        super().__init__(uid_value=uid_value, index_value=index_value, page_uid_value=page_uid_value,
                         condition_string=condition_string)
        self.section_headers_dict = {}
        self.questions_dict = {}

    def add_section_header(self, page_header_object):
        assert isinstance(page_header_object, PageHeaderObject)
        if page_header_object.index not in self.section_headers_dict.keys():
            self.section_headers_dict[page_header_object.index] = page_header_object
        else:
            raise KeyError('Page header with index="' + str(
                page_header_object.index) + '" already present in page_headers_dict on page="' + self.uid + '"')

    def add_question_object(self, question_object):
        assert isinstance(question_object, QuestionObjectClass)
        if question_object.index not in self.questions_dict.keys():
            self.questions_dict[question_object.index] = question_object
            tmp_unique_uids_list = []
            for question_object in self.questions_dict.values():
                if question_object.uid not in tmp_unique_uids_list:
                    tmp_unique_uids_list.append(question_object.uid)
                else:
                    print('Duplicate uid="{0}" found on page="{1}"'.format(question_object.uid, self.uid))
        else:
            raise KeyError(
                'Question with index="{0}", uid="{1}" already present in self.questions_dict on page="{2}"'.format(
                    str(question_object.index), question_object.uid, self.uid))


class UnitHeaderObject(PageHeaderObject):
    def __init__(self, uid_value, page_uid_value, unit_header_type_string, unit_header_text_string, index_value,
                 condition_string):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value,
                         page_header_type_string=unit_header_type_string,
                         page_header_text_string=unit_header_text_string, index_value=index_value,
                         condition_string=condition_string)


class UnitObject(CanHaveConditionWithUid):
    def __init__(self, uid_value, page_uid_value, response_domain_uid_value, index_value=None, condition_string='True',
                 unit_header_objects_list=None):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value,
                         condition_string=condition_string)
        self.unit_header_dict = {}
        self.response_domain_uid = response_domain_uid_value
        self.add_unit_header_objects_list(unit_header_objects_list)

    @property
    def response_domain_uid(self):
        return self._response_domain_uid

    @response_domain_uid.setter
    def response_domain_uid(self, response_domain_uid_value):
        assert isinstance(response_domain_uid_value, str)
        self._response_domain_uid = response_domain_uid_value

    def add_unit_header_objects_list(self, unit_header_objects_list):
        assert isinstance(unit_header_objects_list, list)
        for unit_header_object in unit_header_objects_list:
            assert isinstance(unit_header_object, UnitHeaderObject)
        for unit_header_object in unit_header_objects_list:
            self.unit_header_dict[unit_header_object.index] = unit_header_object
