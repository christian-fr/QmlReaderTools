__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.0.1"
__status__ = "Prototype"
__name__ = "QmlExtractionFunctions"

import QuestionnaireElements


def get_tag_from_page_children_object(page_children_object):
    if hasattr(page_children_object, 'tag'):
        if page_children_object.tag == 'comment':
            return 'comment'
    return page_children_object.tag[page_children_object.tag.rfind('}') + 1:]


def get_uid_attrib_of_source_object(source_object):
    if hasattr(source_object, 'attrib'):
        if 'uid' in source_object.attrib:
            tmp_uid = source_object.attrib['uid']
        else:
            tmp_uid = None
    else:
        tmp_uid = None
    return tmp_uid


def get_text_string_of_source_object(source_object):
    if hasattr(source_object, 'text'):
        tmp_text = source_object.text
    else:
        tmp_text = None
    return tmp_text


def get_condition_string_of_source_object(source_object):
    if hasattr(source_object, 'attrib'):
        if 'visible' in source_object.attrib:
            tmp_condition = source_object.attrib['visible']
        else:
            tmp_condition = None
    else:
        tmp_condition = None
    return tmp_condition


def get_question_header_objects_list(question_source_object, page_uid_value):
    tmp_question_header_objects_list = []
    if hasattr(question_source_object, 'header'):
        tmp_index = 0
        for source_object in question_source_object.header.iterchildren():
            tmp_tag = get_tag_from_page_children_object(source_object)
            tmp_uid = get_uid_attrib_of_source_object(source_object)
            tmp_text = get_text_string_of_source_object(source_object)
            tmp_condition = get_condition_string_of_source_object(source_object)

            tmp_question_header_objects_list.append(
                QuestionnaireElements.QuestionHeaderObject(uid_value=tmp_uid,
                                                           page_uid_value=page_uid_value,
                                                           header_type_string=tmp_tag,
                                                           header_text_string=tmp_text,
                                                           index_value=tmp_index,
                                                           condition_string=tmp_condition))
            tmp_index += 1
        return tmp_question_header_objects_list
    else:
        return []


def get_unit_header_objects_list(unit_object, page_uid_value):
    tmp_question_header_objects_list = []
    if hasattr(unit_object, 'header'):
        tmp_index = 0
        for source_object in unit_object.header.iterchildren():
            tmp_tag = get_tag_from_page_children_object(source_object)
            tmp_uid = get_uid_attrib_of_source_object(source_object)
            tmp_text = get_text_string_of_source_object(source_object)
            tmp_condition = get_condition_string_of_source_object(source_object)

            tmp_question_header_objects_list.append(
                QuestionnaireElements.UnitHeaderObject(uid_value=tmp_uid,
                                                       page_uid_value=page_uid_value,
                                                       unit_header_type_string=tmp_tag,
                                                       unit_header_text_string=tmp_text,
                                                       index_value=tmp_index,
                                                       condition_string=tmp_condition))
            tmp_index += 1
        return tmp_question_header_objects_list
    else:
        return []


def get_question_attribute_value_or_raise_error(source_object, attribute_string, index_value, outer_uid_value,
                                                page_uid_value):
    tmp_question_child_attrib = get_question_child_or_raise_attribute_error(source_object=source_object,
                                                                            child_name_string='attrib',
                                                                            index_value=index_value,
                                                                            outer_uid_value=outer_uid_value,
                                                                            page_uid_value=page_uid_value)
    if attribute_string in tmp_question_child_attrib:
        return tmp_question_child_attrib[attribute_string]
    else:
        raise KeyError(
            'Key "{0}" not found on object with index = "{1}", within outer_uid = "{2}", page = "{3}".'.format(
                attribute_string, index_value, outer_uid_value, page_uid_value))


def get_question_attribute_value_or_return_none(source_object, attribute_string, index_value, outer_uid_value,
                                                page_uid_value):
    tmp_question_child_attrib = get_question_child_or_raise_attribute_error(source_object=source_object,
                                                                            child_name_string='attrib',
                                                                            index_value=index_value,
                                                                            outer_uid_value=outer_uid_value,
                                                                            page_uid_value=page_uid_value)
    if attribute_string in tmp_question_child_attrib:
        return tmp_question_child_attrib[attribute_string]
    else:
        return None


def get_question_child_or_raise_attribute_error(source_object, child_name_string, index_value, outer_uid_value,
                                                page_uid_value):
    pass
    if hasattr(source_object, child_name_string):
        return getattr(source_object, child_name_string)
    else:
        raise AttributeError(
            'Child "{0}" not found on object with index = "{1}", within outer_uid = "{2}", page = "{3}".'.format(
                child_name_string, index_value, outer_uid_value, page_uid_value))


def get_unit_objects_list_from_response_domain_object(response_domain_object, response_domain_uid, page_uid_value):
    tmp_unit_objects_list = []
    tmp_unit_header_objects_list = []

    for child_object in response_domain_object.iterchildren():
        tmp_unit_object = None

        if get_tag_from_page_children_object(child_object) == 'unit':

            tmp_unit_condition = get_condition_string_of_source_object(child_object)
            tmp_unit_uid = get_uid_attrib_of_source_object(child_object)

            if hasattr(child_object, 'header'):
                unit_header_index_counter = 0

                for child_object_of_unit_header in child_object.header.iterchildren():
                    tmp_child_of_unit_header_uid = get_uid_attrib_of_source_object(child_object_of_unit_header)
                    tmp_child_of_unit_header_tag = get_tag_from_page_children_object(child_object_of_unit_header)
                    tmp_child_of_unit_header_text = get_text_string_of_source_object(
                        source_object=child_object_of_unit_header)
                    tmp_child_of_unit_header_condition = get_question_attribute_value_or_return_none(
                        source_object=child_object_of_unit_header, attribute_string='condition',
                        index_value=unit_header_index_counter,
                        outer_uid_value=response_domain_uid, page_uid_value=page_uid_value)

                    tmp_unit_header_object = QuestionnaireElements.UnitHeaderObject(
                        uid_value=tmp_child_of_unit_header_uid, page_uid_value=page_uid_value,
                        unit_header_type_string=tmp_child_of_unit_header_tag,
                        unit_header_text_string=tmp_child_of_unit_header_text, index_value=unit_header_index_counter,
                        condition_string=tmp_child_of_unit_header_condition)

                    unit_header_index_counter += 1

                    tmp_unit_header_objects_list.append(tmp_unit_header_object)

            tmp_unit_object = QuestionnaireElements.UnitObject(uid_value=tmp_unit_uid, page_uid_value=page_uid_value,
                                                               response_domain_uid_value=response_domain_uid,
                                                               index_value=None,
                                                               condition_string=tmp_unit_condition,
                                                               unit_header_objects_list=tmp_unit_header_objects_list)

            tmp_unit_objects_list.append(tmp_unit_object)

    return tmp_unit_objects_list


def get_answer_option_object_from_answer_option_source_object(ao_source_object, question_uid_value, page_uid_value,
                                                              var_name_string,
                                                              ao_index_value, response_domain_uid, unit_uid=None):
    tmp_uid = get_question_attribute_value_or_raise_error(source_object=ao_source_object,
                                                          attribute_string='uid',
                                                          outer_uid_value=question_uid_value,
                                                          page_uid_value=page_uid_value,
                                                          index_value=ao_index_value)

    tmp_ao_value = int(get_question_attribute_value_or_raise_error(source_object=ao_source_object,
                                                                   attribute_string='value',
                                                                   outer_uid_value=question_uid_value,
                                                                   page_uid_value=page_uid_value,
                                                                   index_value=ao_index_value))

    tmp_label_text_value = get_question_attribute_value_or_return_none(source_object=ao_source_object,
                                                                       attribute_string='label',
                                                                       outer_uid_value=question_uid_value,
                                                                       page_uid_value=page_uid_value,
                                                                       index_value=ao_index_value)

    tmp_missing = get_question_attribute_value_or_return_none(source_object=ao_source_object,
                                                              attribute_string='missing',
                                                              outer_uid_value=question_uid_value,
                                                              page_uid_value=page_uid_value,
                                                              index_value=ao_index_value)
    if tmp_missing is not None:
        if tmp_missing.lower() == "true":
            tmp_missing_bool = True
        else:
            tmp_missing_bool = False
    else:
        tmp_missing_bool = False

    tmp_condition = get_question_attribute_value_or_return_none(source_object=ao_source_object,
                                                                attribute_string='visible',
                                                                outer_uid_value=question_uid_value,
                                                                page_uid_value=page_uid_value,
                                                                index_value=ao_index_value)

    tmp_answer_option_object = QuestionnaireElements.AnswerOptionObject(uid_value=tmp_uid,
                                                                        question_uid_value=question_uid_value,
                                                                        page_uid_value=page_uid_value,
                                                                        var_name_string=var_name_string,
                                                                        index_value=ao_index_value,
                                                                        response_domain_uid=response_domain_uid,
                                                                        label_text_value=tmp_label_text_value,
                                                                        missing_bool=tmp_missing_bool,
                                                                        ao_value=tmp_ao_value,
                                                                        condition_string=tmp_condition,
                                                                        belongs_to_unit_uid=unit_uid)
    return tmp_answer_option_object


def get_question_answer_options_objects_unit_objects_list(question_source_object, page_uid_value, question_uid_value):
    tmp_response_domain_object = get_question_child_or_raise_attribute_error(source_object=question_source_object,
                                                                             child_name_string='responseDomain',
                                                                             index_value=None,
                                                                             outer_uid_value=question_uid_value,
                                                                             page_uid_value=page_uid_value)

    tmp_response_domain_uid = get_question_attribute_value_or_raise_error(source_object=tmp_response_domain_object,
                                                                          attribute_string='uid',
                                                                          index_value=None,
                                                                          outer_uid_value=question_uid_value,
                                                                          page_uid_value=page_uid_value)

    tmp_var_name_string = get_question_attribute_value_or_raise_error(source_object=tmp_response_domain_object,
                                                                      attribute_string='variable',
                                                                      index_value=None,
                                                                      outer_uid_value=question_uid_value,
                                                                      page_uid_value=page_uid_value)

    # first iteration: find units,
    tmp_unit_objects_list = get_unit_objects_list_from_response_domain_object(
        response_domain_object=tmp_response_domain_object, response_domain_uid=tmp_response_domain_uid,
        page_uid_value=page_uid_value)

    # second iteration: find all answer options, set their indices and units
    tmp_answer_options_list = []
    tmp_ao_index = 0

    for ao_source_object in tmp_response_domain_object.iterchildren():
        tmp_ao_source_object_uid = get_question_attribute_value_or_raise_error(source_object=ao_source_object,
                                                                   attribute_string='uid',
                                                                   outer_uid_value=question_uid_value,
                                                                   page_uid_value=page_uid_value,
                                                                   index_value=tmp_ao_index)

        tmp_ao_source_object_tag = get_tag_from_page_children_object(ao_source_object)


        # if UNIT found
        if tmp_ao_source_object_tag == 'unit':
            tmp_unit_uid = tmp_ao_source_object_uid

        # if regular ANSWER OPTION found
        elif tmp_ao_source_object_tag == 'answerOption':
            tmp_unit_uid = None

        # if tag not recognized
        else:
            raise ValueError('Object not recognized: uid "{0}", tag "{1}", response domain uid "{2}" on page "{3}"'.format(tmp_ao_source_object_uid, tmp_ao_source_object_tag, tmp_response_domain_uid, page_uid_value))




        # tmp_answer_options_list.append(tmp_answer_option_object)
        tmp_ao_index += 1

    return tmp_answer_options_list, tmp_unit_objects_list

































































