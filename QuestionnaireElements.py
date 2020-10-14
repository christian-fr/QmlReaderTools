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
        assert isinstance(question_or_section_object, QuestionObjectClass) or isinstance(question_or_section_object, PageHeaderObject)
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


class QuestionHeaderObject(HeaderObject):
    def __init__(self, uid_value, page_uid_value, header_type_string, header_text_string, index_value,
                 condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         header_text_string=header_text_string, index_value=index_value)
        self.allowed_header_types_list = ['question', 'instruction', 'introduction']
        self.header_type = header_type_string
        self.text = header_text_string

    @property
    def header_type(self):
        return self.__header_type

    @header_type.setter
    def header_type(self, header_type_string):
        try:
            assert isinstance(header_type_string, str) and header_type_string in self.allowed_header_types_list
        except AssertionError:
            raise TypeError(
                'Object with uid="{0}" is of header_type="{1}", not of allowed_header_types: "{2}"'.format(self.uid,
                                                                                                           header_type_string,
                                                                                                           str(
                                                                                                               self.allowed_header_types_list)))
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
    def __init__(self, uid_value, page_uid_value, var_name_string, index_value, response_domain_uid,
                 label_text_value=None, missing_bool=False, ao_value=None, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        self.label_text = label_text_value
        self.var_name = var_name_string
        self.response_domain_uid = response_domain_uid
        self.missing_flag = missing_bool
        self.value = ao_value

    def __str__(self):
        return str((self.page_uid, str(self.index), self.uid, self.label_text, str(self.value)))

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


class PageBody(UniqueObject):
    def __init__(self, uid_value):
        super().__init__(uid_value=uid_value, index_value=0)

# class SectionObjectBaseClass(CanHaveConditionWithUid):
#     def __init__(self, uid_value, page_uid_value, index_value, condition_string='True'):
#         super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value,
#                          condition_string=condition_string)

class QuestionObjectBaseClass(CanHaveConditionWithUid):
    def __init__(self, uid_value, page_uid_value, index_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, index_value=index_value,
                         condition_string=condition_string)
        self.variables_dict = {}
        self.question_header_dict = {}
        self.answer_option_dict = {}

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
    def __init__(self, uid_value, page_uid_value, index_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        self.item_dict = {}

    def add_item(self, item_object):
        assert isinstance(item_object, ItemObject)
        if item_object.uid not in self.item_dict.keys():
            self.item_dict[item_object.uid] = item_object
        else:
            raise KeyError(
                'Item with uid="' + item_object.uid + '" already present in question with uid="' + self.uid + '" on page="' + self.page_uid + '"')


class QuestionSingleChoiceObject(QuestionObjectClass):
    def __init__(self, uid_value, page_uid_value, index_value, answer_option_objects_list,
                 question_header_objects_list=None, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)
        self.variables_list = []
        self.add_answer_option_objects_list(answer_option_objects_list)
        self.add_question_header_objects_list(question_header_objects_list)

    def add_answer_option_objects_list(self, answer_option_objects_list):
        assert isinstance(answer_option_objects_list, list)
        for answer_option_object in answer_option_objects_list:
            assert isinstance(answer_option_object, AnswerOptionObject)
        for answer_option_object in answer_option_objects_list:
            self.add_answer_option(answer_option_object=answer_option_object)

    def add_question_header_objects_list(self, question_header_objects_list):
        assert isinstance(question_header_objects_list, list)
        for question_header_object in question_header_objects_list:
            assert isinstance(question_header_object, QuestionHeaderObject)
            self.add_question_header(question_header_object=question_header_object)


class ItemObject(QuestionObjectBaseClass):
    def __init__(self, uid_value, page_uid_value, index_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string,
                         index_value=index_value)


class Prefix:
    def __init__(self):
        pass


class Postfix:
    def __init__(self):
        pass


class Unit:
    def __init__(self):
        pass


class Section(CanHaveConditionWithUid):
    def __init__(self, uid_value, index_value, page_uid_value, condition_string):
        super().__init__(uid_value=uid_value, index_value=index_value, page_uid_value=page_uid_value, condition_string=condition_string)
        self.section_headers_dict ={}
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

# ao1 = AnswerOptionObject(uid_value='ao1', page_uid_value='A01', var_name_string='v1', index_value=0, response_domain_uid='rd', label_text_value='label1', ao_value=1)
# ao2 = AnswerOptionObject(uid_value='ao2', page_uid_value='A01', var_name_string='v1', index_value=1, response_domain_uid='rd', label_text_value='label2', ao_value=2)
# ao3 = AnswerOptionObject(uid_value='ao3', page_uid_value='A01', var_name_string='v1', index_value=2, response_domain_uid='rd', label_text_value='label3', ao_value=3)
#
#
# qh = QuestionHeaderObject(uid_value='ti1', page_uid_value='A01', index_value=0, header_text_string='Header strings sind schön.', header_type_string='question')
#
# qsc1 = QuestionSingleChoice(uid_value='qsc1', page_uid_value='A01', index_value=0, answer_option_objects_list=[ao1, ao2, ao3], question_header_objects_list=[qh], condition_string='1 == 1')
# qsc2 = QuestionSingleChoice(uid_value='qsc1', page_uid_value='A01', index_value=1, answer_option_objects_list=[ao1, ao2, ao3], question_header_objects_list=[qh], condition_string='1 == 2')
#
# page1 = PageObject(uid_value='A01', index_value=0, declared=True)
# page1.add_question_object(qsc1)
# page1.add_question_object(qsc2)
