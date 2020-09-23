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



class CanHaveCondition(OnPageObjectWithUid):
    def __init__(self, uid_value, page_uid_value, condition_string = 'True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value)
        self.condition = ConditionObject(condition_string=condition_string)

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition_string):
        assert isinstance(condition_string, str)
        self.__condition = condition_string


class VariableObject():
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
        assert isinstance(var_name, str) or isinstance(var_name)
        if var_name in self.dict_of_variables.keys():
            self.dict_of_variables[var_name].set_value(value)


class Pages:
    def __init__(self):
        self.dict_of_pages = {}

    def get_all_pages_list(self):
        return list(self.dict_of_pages.keys())

    def get_page_by_uid(self, uid):
        assert isinstance(uid, str)
        if uid in self.dict_of_pages.keys():
            return self.dict_of_pages[uid]
        else:
            print('Page "' + str(uid) + '" not found.')

    def add_page(self, uid):
        pass


class Questions(OnPageObjectWithoutUid):
    def __init__(self, page_uid_value):
        super().__init__(page_uid_value=page_uid_value)
        self.dict_of_questions = {}

    def add_question(self, question_object):
        assert isinstance(question_object, QuestionObject)
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



class AnswerOption:
    def __init__(self):
        pass


class QuestionHeaderObject(CanHaveCondition):
    def __init__(self, uid_value, page_uid_value, header_type_string, header_text_string, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value, condition_string=condition_string)
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


class QuestionObject(CanHaveCondition):
    def __init__(self, uid_value, page_uid_value, condition_string='True'):
        super().__init__(uid_value=uid_value, page_uid_value=page_uid_value)
        self.variables_dict = {}
        self.condition = condition_string
        self.question_header_dict = {}

    def add_question_header(self, QuestionHeaderObject):

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


class QuestionSingleChoice(QuestionObject):
    def __init__(self, uid_value, page_uid_value, answer_options, question_header=None, condition_string='True'):
        super().__init__(uid_value)
        self.variables_list = []
        self.question_header_dict = {}

        self.answer_options = []


class QuestionHeader:
    def __init__(self):
        pass


class Title:
    def __init__(self):
        pass


class Item:
    def __init__(self):
        pass


class Labels:
    def __init__(self):
        pass


class Prefix:
    def __init__(self):
        pass


class Postfix:
    def __init__(self):
        pass


class Unit:
    def __init__(self):
        pass


class ResponseDomain:
    def __init__(self):
        pass


class Section:
    def __init__(self):
        pass


class ConditionObject:
    def __init__(self, condition_string):
        self.condition = None
        self.python_condition = None
        self.set_condition(condition_string)

    def evaluate(self):
        if self.python_condition is not None:
            pass
            # Todo: evaluate expression!
            return True
            return False
        else:
            raise NotImplementedError('Condition: "' + str(self.condition) + '" has not yet been translated into python logic!')

    def set_condition(self, condition):
        assert isinstance(condition, str) or isinstance(condition, bool) or condition is None
        self.condition = condition

    def translate_condition_to_python_logic:
        pass