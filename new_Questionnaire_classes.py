class UniqueObject:
    def __init__(self, uid_value):
        self.uid = uid_value

    @property
    def uid(self):
        return self.__uid

    @uid.setter
    def uid(self, uid_string):
        assert isinstance(uid_string, str)
        self.__uid = uid_string


class OnPageObjectWithUid(UniqueObject):
    def __init__(self, uid_value, page_uid_value):
        super().__init__(uid_value=uid_value)
        self.page_uid = page_uid_value

    @property
    def page_uid(self):
        return self.__page_uid

    @page_uid.setter
    def page_uid(self, page_uid_value):
        assert isinstance(page_uid_value, str)
        self.__page_uid = page_uid_value


class OnPageObjectWithoutUid:
    def __init__(self, page_uid_value):
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
        self.condition = None
        self.python_condition = None
        self.condition(condition_string)

    def evaluate(self):
        if self.python_condition is not None:
            pass
            # Todo: evaluate expression!
            return True
            return False
        else:
            raise NotImplementedError('Condition: "' + str(self.condition) + '" has not yet been translated into python logic!')

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition_string):
        assert isinstance(condition_string, str) or isinstance(condition_string, bool) or condition_string is None
        self.__condition = condition_string

    def translate_condition_to_python_logic(self):
        pass


class CanHaveCondition(OnPageObjectWithUid):
    def __init__(self, uid_value, page_uid_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value)
        self.condition = ConditionObject(condition_string=condition_string)

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition_string):
        assert isinstance(condition_string, str)
        self.__condition = condition_string


class VariableObject:
    def __init__(self, name_string, var_type_string):
        self._allowed_var_types = ['string', 'boolean', 'singleChoiceAnswerOption', 'number']
        self.name = name_string
        self.var_type = var_type_string
        self.var_value = None

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
    def __init__(self, uid_value, declared=True):
        super().__init__(uid_value=uid_value)

        self.declared = declared

        self.page_headers_dict = {}
        self.sources_dict = {}
        self.transitions_dict = {}
        self.triggers_dict = {}
        self.questions_dict = {}

    @property
    def declared(self):
        return self.__declared

    @declared.setter
    def declared(self, declared_bool):
        assert isinstance(declared_bool, bool)
        self.__declared = declared_bool

    def get_all_var_names_list(self):
        # ToDo: yet to be implemented
        raise NotImplementedError()

    def get_all_duplicate_var_names_list(self):
        # ToDo: yet to be implemented
        raise NotImplementedError()

    def get_all_sources_list(self):
        return list(self.sources_dict.keys())

    def get_all_transitions_list(self):
        return list(self.transitions_dict)

    def get_all_triggers_list(self):
        # ToDo: display var_names of variable trigger
        return list(self.triggers_dict.keys())

    def get_all_questions_list(self):
        return list(self.questions_dict.keys())

    def add_source(self, source_object):
        assert isinstance(source_object, SourceObject)
        if source_object.index not in self.sources_dict.keys():
            self.sources_dict[source_object.index] = source_object
        else:
            raise KeyError('Source with index="' + str(source_object.index) + '" already present in sources_dict of page="' + self.uid + '"')

    def add_transition(self, transition_object):
        assert isinstance(transition_object, TransitionObject)
        if transition_object.index not in self.transitions_dict.keys():
            self.transitions_dict[transition_object.index] = transition_object
        else:
            raise KeyError('Transition with index="' + str(transition_object.index) + '" already present in transitions_dict on page="' + self.uid + '"')

    def add_trigger(self, trigger_object):
        assert isinstance(trigger_object, TriggerObject)
        if trigger_object.index not in self.triggers_dict.keys():
            self.triggers_dict[trigger_object.index] = trigger_object
        else:
            raise KeyError('Transition with index="' + str(trigger_object.index) + '" already present in triggers_dict on page="' + self.uid + '"')

    def add_page_header(self, page_header_object):
        assert isinstance(page_header_object, PageHeaderObject)
        if page_header_object.index not in self.page_headers_dict.keys():
            self.page_headers_dict[page_header_object.index] = page_header_object
        else:
            raise KeyError('Page header with index="' + str(page_header_object.index) + '" already present in page_headers_dict on page="' + self.uid + '"')


class TransitionObject(CanHaveCondition):
    def __init__(self, page_uid_value, target_page_uid_value, index_int, condition_string='True'):
        super().__init__(uid_value=None, page_uid_value=page_uid_value, condition_string=condition_string)
        self.target_page_uid = target_page_uid_value
        self.condition = condition_string
        self.index = index_int

        pass

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index_int):
        assert isinstance(index_int, int)
        self.__index = index_int

    @property
    def target_page_uid(self):
        return self.target_page_uid

    @target_page_uid.setter
    def target_page_uid(self, target_page_uid_value):
        assert isinstance(target_page_uid_value, str)
        self.__target_page_uid = target_page_uid_value


class SourceObject(CanHaveCondition):
    def __init__(self, page_uid_value, source_page_uid_value, index_int, condition_string='True'):
        super().__init__(uid_value=None, page_uid_value=page_uid_value, condition_string=condition_string)
        # ToDo: finish writing this class with @property getters / setters
        self.source_page_uid = source_page_uid_value
        self.page_uid = page_uid_value
        self.condition = condition_string
        self.index = index_int
        pass

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index_int):
        assert isinstance(index_int, int)
        self.__index = index_int

    @property
    def source_page_uid(self):
        return self.__source_page_uid

    @source_page_uid.setter
    def source_page_uid(self, source_page_uid_string):
        assert isinstance(source_page_uid_string, str)
        self.__source_page_uid = source_page_uid_string


class TriggerObject(CanHaveCondition):
    def __init__(self, page_uid_value, index_int, var_name_string, value_string, condition_string='True'):
        # ToDo: finish writing this class with @property getters / setters
        super().__init__(uid_value=None, page_uid_value=page_uid_value, condition_string=condition_string)
        self.condition = condition_string
        self.var_name = var_name_string
        self.index = index_int
        self.value = value_string
        pass

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index_int):
        assert isinstance(index_int, int)
        self.__index = index_int

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


class Questions(OnPageObjectWithoutUid):
    def __init__(self, page_uid_value):
        super().__init__(page_uid_value=page_uid_value)
        self.dict_of_questions = {}

    def add_question(self, question_object):
        assert isinstance(question_object, QuestionObjectClass)
        assert question_object.page_uid == self.page_uid
        if question_object.uid not in self.dict_of_questions.keys():
            self.dict_of_questions[question_object.uid] = question_object
        else:
            raise KeyError('Question uid="' + question_object.uid + '" already present on page="' + self.page_uid + '"')

    def get_question_object_from_uid(self, uid_value):
        assert isinstance(uid_value, str)
        if uid_value in self.dict_of_questions.keys():
            return
        else:
            raise KeyError('No question with uid="' + uid_value + '" found on page="' + self.page_uid + '"')

    def get_all_question_uids_list(self):
        return list(self.dict_of_questions.keys())


class PageHeaders:
    def __init__(self):
        self.dict_of_page_headers = {}


class HeaderObject(CanHaveCondition):
    def __init__(self, uid_value, page_uid_value, header_text_string, index_int, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string)
        self.allowed_header_types = ['None']
        self.text = header_text_string
        self.index = index_int

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
    def index(self):
        return self.__index

    @index.setter
    def index(self, index_int):
        assert isinstance(index_int, int)
        self.__index = index_int

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, page_header_text_string):
        assert isinstance(page_header_text_string, str)
        self.__text = page_header_text_string


class QuestionHeaderObject(HeaderObject):
    def __init__(self, uid_value, page_uid_value, header_type_string, header_text_string, index_int, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string, header_text_string=header_text_string, index_int=index_int)
        self._allowed_header_types = ['question', 'instruction', 'introduction']
        self.header_type = header_type_string
        self.text = header_text_string

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, header_text_string):
        assert isinstance(header_text_string, str)
        self.__text = header_text_string

    @property
    def header_type(self):
        return self.__header_type

    @header_type.setter
    def header_type(self, header_type_string):
        assert isinstance(header_type_string, str) and header_type_string in self._allowed_header_types
        self.__header_type = header_type_string


class PageHeaderObject(HeaderObject):
    def __init__(self, uid_value, page_uid_value, page_header_type_value, page_header_text_string, index_int, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string, header_text_string=page_header_text_string, index_int=index_int)
        self._allowed_page_header_types = ['title']
        self.dict_of_page_headers = {}
        self.page_header_type = page_header_type_value
        self.index = index_int
        pass

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, index_int):
        assert isinstance(index_int, int)
        self.__index = index_int

    @property
    def page_header_type(self):
        return self.__page_header_type

    @page_header_type.setter
    def page_header_type(self, page_header_type_value):
        assert isinstance(page_header_type_value, str) and page_header_type_value in self._allowed_page_header_types
        self.__page_header_type = page_header_type_value


class AnswerOptionObject(CanHaveCondition):
    def __init__(self, uid_value, page_uid_value, var_name_string, response_domain_uid, label_text_value=None, missing_bool=False, ao_value=None, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string)
        self.label_text = label_text_value
        self.var_name = var_name_string
        self.response_domain_uid = response_domain_uid
        self.missing_flag = missing_bool
        self.value = ao_value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, ao_value):
        assert isinstance(ao_value, int) or ao_value is None
        self.__value = ao_value

    @property
    def missing_flag(self):
        return self.__missing_flag

    @missing_flag.setter
    def missing_flag(self, missing_bool):
        assert isinstance(missing_bool, bool)
        self.__missing_flag = missing_bool

    @property
    def response_domain_uid(self):
        return self.__response_domain_uid

    @response_domain_uid.setter
    def response_domain_uid(self, response_domain_uid_value):
        assert isinstance(response_domain_uid_value, str)
        self.__response_domain_uid = response_domain_uid_value

    @property
    def var_name(self):
        return self.__var_name

    @var_name.setter
    def var_name(self, var_name_string):
        assert isinstance(var_name_string, str)
        self.__var_name = var_name_string

    @property
    def label_text(self):
        return self.__label_text

    @label_text.setter
    def label_text(self, label_text_value):
        assert isinstance(label_text_value, str) or label_text_value is None
        self.__label_text = label_text_value



class QuestionObjectBaseClass(CanHaveCondition):
    def __init__(self, uid_value, page_uid_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value)
        self.variables_dict = {}
        self.condition = condition_string
        self.question_header_dict = {}

    def add_question_header(self, question_header_object):
        assert isinstance(question_header_object, QuestionHeaderObject)
        if question_header_object.uid not in self.question_header_dict.keys():
            self.question_header_dict[question_header_object.uid] = question_header_object
        else:
            raise KeyError('QuestionHeaderObject with uid="' + question_header_object.uid + '" already in question_header_dict of question with uid="' + self.uid + '" on page="' + self.page_uid +'"')

    def get_all_variables_list(self):
        return list(self.variables_dict.keys())

    def get_variable_from_var_name(self, var_name_string):
        assert isinstance(var_name_string, str) and var_name_string in self.variables_dict.keys()
        return self.variables_dict[var_name_string]

    def add_variable(self, variable_object):
        assert isinstance(variable_object, VariableObject)
        if variable_object.name not in self.variables_dict.keys():
            self.variables_dict[variable_object.name] = variable_object
        else:
            print('Variable "' + variable_object.name + '" already found in Question.variables_dict!')

    @property
    def page_uid(self):
        return self.__page_uid

    @page_uid.setter
    def page_uid(self, page_uid_value):
        assert isinstance(page_uid_value, str)
        self.__page_uid = page_uid_value


class QuestionObjectClass(QuestionObjectBaseClass):
    def __init__(self, uid_value, page_uid_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string)
        self.item_dict = {}

    def add_item(self, item_object):
        assert isinstance(item_object, ItemObject)
        if item_object.uid not in self.item_dict.keys():
            self.item_dict[item_object.uid] = item_object
        else:
            raise KeyError('Item with uid="' + item_object.uid + '" already present in question with uid="' + self.uid + '" on page="' + self.page_uid + '"')


class QuestionSingleChoice(QuestionObjectClass):
    def __init__(self, uid_value, page_uid_value, answer_options, question_header=None, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=page_uid_value)
        self.variables_list = []
        self.question_header_dict = {}
        self.answer_options_dict = {}


class ItemObject(QuestionObjectBaseClass):
    def __init__(self, uid_value, page_uid_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string)


class Prefix:
    def __init__(self):
        pass


class Postfix:
    def __init__(self):
        pass


class Unit:
    def __init__(self):
        pass


class Section:
    def __init__(self):
        pass


