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


def get_response_domain_header_objects_list(question_source_object, page_uid_value):
    tmp_question_header_objects_list = []
    if hasattr(question_source_object, 'header'):
        tmp_index = 0
        for source_object in question_source_object.header.iterchildren():
            tmp_tag = get_tag_from_page_children_object(source_object)
            tmp_uid = get_uid_attrib_of_source_object(source_object)
            tmp_text = get_text_string_of_source_object(source_object)
            tmp_condition = get_condition_string_of_source_object(source_object)

            tmp_question_header_objects_list.append(
                QuestionnaireElements.ResponseDomainHeaderObject(uid_value=tmp_uid,
                                                                 page_uid_value=page_uid_value,
                                                                 header_type_string=tmp_tag,
                                                                 header_text_string=tmp_text,
                                                                 index_value=tmp_index,
                                                                 condition_string=tmp_condition))
            tmp_index += 1
        return tmp_question_header_objects_list
    else:
        return []


def get_unit_header_objects_list(source_object, page_uid_value):
    tmp_question_header_objects_list = []
    if hasattr(source_object, 'header'):
        tmp_index = 0
        for unit_source_object in source_object.header.iterchildren():
            tmp_tag = get_tag_from_page_children_object(unit_source_object)
            tmp_uid = get_uid_attrib_of_source_object(unit_source_object)
            tmp_text = get_text_string_of_source_object(unit_source_object)
            tmp_condition = get_condition_string_of_source_object(unit_source_object)

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


def get_question_child_or_return_none(source_object, child_name_string):
    pass
    if hasattr(source_object, child_name_string):
        return getattr(source_object, child_name_string)
    else:
        return None


def get_question_child_or_raise_attribute_error(source_object, child_name_string, index_value, outer_uid_value,
                                                page_uid_value):
    tmp_question_child = get_question_child_or_return_none(source_object=source_object,
                                                           child_name_string=child_name_string)
    if tmp_question_child is not None:
        return tmp_question_child
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


def extract_question_mqsc_from_source_object_or_return_error(source_object, page_uid_value,
                                                             index_value):
    tmp_question_uid = get_uid_attrib_of_source_object(source_object)

    tmp_question_header_objects_list = get_question_header_objects_list(
        question_source_object=source_object, page_uid_value=page_uid_value)

    tmp_condition_string = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                       attribute_string='visible',
                                                                       index_value=index_value,
                                                                       page_uid_value=page_uid_value,
                                                                       outer_uid_value=None)

    tmp_response_domain_object = get_question_child_or_raise_attribute_error(source_object=source_object,
                                                                             child_name_string='responseDomain',
                                                                             index_value=None,
                                                                             outer_uid_value=tmp_question_uid,
                                                                             page_uid_value=page_uid_value)

    tmp_is_show_values = get_question_attribute_value_or_return_none(source_object=tmp_response_domain_object,
                                                                     attribute_string='isShowValues',
                                                                     page_uid_value=page_uid_value, index_value=None,
                                                                     outer_uid_value=tmp_question_uid)

    tmp_no_response_options = get_question_attribute_value_or_return_none(source_object=tmp_response_domain_object,
                                                                          attribute_string='noResponseOptions',
                                                                          page_uid_value=page_uid_value,
                                                                          index_value=None,
                                                                          outer_uid_value=tmp_question_uid)

    tmp_list_of_mqsc_item_objects, tmp_list_of_mqsc_response_domain_header_objects = extract_mqsc_item_objects_from_response_domain_source_object_or_return_error(
        source_object=tmp_response_domain_object,
        page_uid_value=page_uid_value,
        outer_uid_value=tmp_question_uid)

    return QuestionnaireElements.QuestionMatrixQuestionSingleChoiceObject(uid_value=tmp_question_uid,
                                                                          page_uid_value=page_uid_value,
                                                                          index_value=index_value,
                                                                          mqsc_response_domain_header_objects_list=tmp_list_of_mqsc_response_domain_header_objects,
                                                                          condition_string=tmp_condition_string,
                                                                          mqsc_item_objects_list=tmp_list_of_mqsc_item_objects,
                                                                          question_header_objects_list=tmp_question_header_objects_list)


def extract_mqsc_item_objects_from_response_domain_source_object_or_return_error(source_object,
                                                                                 page_uid_value,
                                                                                 outer_uid_value):
    # tmp_response_domain_uid = get_question_attribute_value_or_raise_error(source_object=source_object,
    #                                                                       attribute_string='uid',
    #                                                                       index_value=None,
    #                                                                       outer_uid_value=outer_uid_value,
    #                                                                       page_uid_value=page_uid_value)

    tmp_list_of_mqsc_response_domain_header_objects = get_response_domain_header_objects_list(
        question_source_object=source_object, page_uid_value=page_uid_value)

    tmp_list_of_mqsc_item_objects = []
    tmp_item_counter = 0
    for child_source_object in source_object.iterchildren():
        tmp_tag = get_tag_from_page_children_object(child_source_object)
        if tmp_tag == 'header':
            continue
        elif tmp_tag == 'item':
            tmp_item_object = extract_question_single_choice_object_from_source_object_or_return_error(
                source_object=child_source_object, page_uid_value=page_uid_value, index_value=tmp_item_counter)
            tmp_list_of_mqsc_item_objects.append(tmp_item_object)
            tmp_item_counter += 1
            pass
    return tmp_list_of_mqsc_item_objects, tmp_list_of_mqsc_response_domain_header_objects


def extract_question_multiple_choice_object_from_source_object_or_return_error(source_object, page_uid_value,
                                                                               index_value):
    tmp_question_uid = get_uid_attrib_of_source_object(source_object)

    tmp_question_header_objects_list = get_question_header_objects_list(
        question_source_object=source_object, page_uid_value=page_uid_value)

    tmp_answer_option_objects_list, tmp_unit_objects_list, tmp_response_domain_type = get_question_answer_options_objects_unit_objects_list(
        question_source_object=source_object, page_uid_value=page_uid_value,
        question_uid_value=tmp_question_uid)

    tmp_condition_string = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                       attribute_string='visible',
                                                                       index_value=index_value,
                                                                       page_uid_value=page_uid_value,
                                                                       outer_uid_value=None)

    return QuestionnaireElements.QuestionMultipleChoiceObject(uid_value=tmp_question_uid,
                                                              page_uid_value=page_uid_value,
                                                              index_value=index_value,
                                                              answer_option_objects_list=tmp_answer_option_objects_list,
                                                              question_header_objects_list=tmp_question_header_objects_list,
                                                              condition_string=tmp_condition_string,
                                                              list_of_units=tmp_unit_objects_list)


def extract_question_single_choice_object_from_source_object_or_return_error(source_object, page_uid_value,
                                                                             index_value, outer_uid=None):
    tmp_question_uid = get_uid_attrib_of_source_object(source_object)

    tmp_question_header_objects_list = get_question_header_objects_list(
        question_source_object=source_object,
        page_uid_value=page_uid_value)

    # get answer_options_list and unit_objects_list
    tmp_answer_option_objects_list, tmp_unit_objects_list, tmp_response_domain_type = get_question_answer_options_objects_unit_objects_list(
        question_source_object=source_object,
        page_uid_value=page_uid_value,
        question_uid_value=tmp_question_uid)

    tmp_condition_string = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                       attribute_string='visible',
                                                                       index_value=index_value,
                                                                       page_uid_value=page_uid_value,
                                                                       outer_uid_value=None)

    return QuestionnaireElements.QuestionSingleChoiceObject(
        uid_value=tmp_question_uid,
        page_uid_value=page_uid_value,
        index_value=index_value,
        answer_option_objects_list=tmp_answer_option_objects_list,
        question_header_objects_list=tmp_question_header_objects_list,
        condition_string=tmp_condition_string,
        list_of_units=tmp_unit_objects_list,
        response_domain_type_value=tmp_response_domain_type,
        outer_uid_value=outer_uid)


def extract_question_open_object_from_source_object_or_return_error(source_object, page_uid_value, index_value,
                                                                    outer_uid_value):
    tmp_question_open_object = extract_question_open_object_from_source_object_or_return_none(
        source_object=source_object,
        page_uid_value=page_uid_value,
        index_value=index_value,
        outer_uid_value=outer_uid_value)
    if tmp_question_open_object is not None:
        return tmp_question_open_object
    else:
        raise AttributeError(
            'No questionOpen found on page uid "{0}", index "{1}", outer uid "{2}"'.format(page_uid_value,
                                                                                           index_value,
                                                                                           outer_uid_value))


def extract_question_open_object_from_source_object_or_return_none(source_object, page_uid_value, index_value,
                                                                   outer_uid_value):
    if get_tag_from_page_children_object(source_object) == 'questionOpen':
        tmp_uid = get_question_attribute_value_or_raise_error(source_object=source_object,
                                                              attribute_string='uid',
                                                              outer_uid_value=outer_uid_value,
                                                              page_uid_value=page_uid_value,
                                                              index_value=None)
        tmp_var_name_string = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                          attribute_string='variable',
                                                                          outer_uid_value=outer_uid_value,
                                                                          page_uid_value=page_uid_value,
                                                                          index_value=index_value)
        tmp_condition_string = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                           attribute_string='condition',
                                                                           outer_uid_value=outer_uid_value,
                                                                           page_uid_value=page_uid_value,
                                                                           index_value=index_value)
        tmp_small_option = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                       attribute_string='smallOption',
                                                                       outer_uid_value=outer_uid_value,
                                                                       page_uid_value=page_uid_value,
                                                                       index_value=index_value)
        tmp_rows = get_question_attribute_value_or_return_none(source_object=source_object,
                                                               attribute_string='rows',
                                                               outer_uid_value=outer_uid_value,
                                                               page_uid_value=page_uid_value,
                                                               index_value=index_value)
        tmp_columns = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                  attribute_string='columns',
                                                                  outer_uid_value=outer_uid_value,
                                                                  page_uid_value=page_uid_value,
                                                                  index_value=index_value)
        tmp_max_value = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                    attribute_string='maxValue',
                                                                    outer_uid_value=outer_uid_value,
                                                                    page_uid_value=page_uid_value,
                                                                    index_value=index_value)
        tmp_min_value = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                    attribute_string='minValue',
                                                                    outer_uid_value=outer_uid_value,
                                                                    page_uid_value=page_uid_value,
                                                                    index_value=index_value)
        tmp_max_length = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                     attribute_string='maxLength',
                                                                     outer_uid_value=outer_uid_value,
                                                                     page_uid_value=page_uid_value,
                                                                     index_value=index_value)
        tmp_question_open_type = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                             attribute_string='type',
                                                                             outer_uid_value=outer_uid_value,
                                                                             page_uid_value=page_uid_value,
                                                                             index_value=index_value)
        tmp_validation_message = get_question_attribute_value_or_return_none(source_object=source_object,
                                                                             attribute_string='validationMessage',
                                                                             outer_uid_value=outer_uid_value,
                                                                             page_uid_value=page_uid_value,
                                                                             index_value=index_value)
        tmp_size = get_question_attribute_value_or_return_none(source_object=source_object,
                                                               attribute_string='size',
                                                               outer_uid_value=outer_uid_value,
                                                               page_uid_value=page_uid_value,
                                                               index_value=index_value)

        tmp_prefix_label_object_list = []
        tmp_postfix_label_object_list = []

        tmp_prefix_index = 0
        tmp_postfix_index = 0

        tmp_question_open_question_header_objects_list = get_question_header_objects_list(
            question_source_object=source_object, page_uid_value=page_uid_value)

        for child_of_source_object in source_object.iterchildren():
            if get_tag_from_page_children_object(child_of_source_object) == 'prefix':
                if hasattr(child_of_source_object, 'label'):
                    for child_label_object in child_of_source_object.iterchildren():
                        tmp_prefix_uid = get_question_attribute_value_or_raise_error(
                            source_object=child_label_object,
                            attribute_string='uid',
                            outer_uid_value=outer_uid_value,
                            page_uid_value=page_uid_value,
                            index_value=index_value)
                        tmp_label_text = get_text_string_of_source_object(child_label_object)
                        tmp_condition = get_condition_string_of_source_object(child_label_object)

                        tmp_prefix_label_object = QuestionnaireElements.PrefixLabelObject(uid=tmp_prefix_uid,
                                                                                          page_uid_value=page_uid_value,
                                                                                          label_text_value=tmp_label_text,
                                                                                          condition_string=tmp_condition,
                                                                                          index_value=tmp_prefix_index)
                        tmp_prefix_index += 1
                        tmp_prefix_label_object_list.append(tmp_prefix_label_object)

            if get_tag_from_page_children_object(child_of_source_object) == 'postfix':
                if hasattr(child_of_source_object, 'label'):
                    for child_label_object in child_of_source_object.iterchildren():
                        tmp_postfix_uid = get_question_attribute_value_or_raise_error(
                            source_object=child_label_object,
                            attribute_string='uid',
                            outer_uid_value=outer_uid_value,
                            page_uid_value=page_uid_value,
                            index_value=index_value)
                        tmp_label_text = get_text_string_of_source_object(child_label_object)
                        tmp_condition = get_condition_string_of_source_object(child_label_object)

                        tmp_postfix_label_object = QuestionnaireElements.PostfixLabelObject(uid=tmp_postfix_uid,
                                                                                            page_uid_value=page_uid_value,
                                                                                            label_text_value=tmp_label_text,
                                                                                            condition_string=tmp_condition,
                                                                                            index_value=tmp_postfix_index)
                        tmp_postfix_index += 1
                        tmp_postfix_label_object_list.append(tmp_postfix_label_object)

        tmp_question_open_object = QuestionnaireElements.QuestionOpen(uid_value=tmp_uid,
                                                                      page_uid_value=page_uid_value,
                                                                      index_value=index_value,
                                                                      var_name_string=tmp_var_name_string,
                                                                      condition_string=tmp_condition_string,
                                                                      small_option=tmp_small_option, rows=tmp_rows,
                                                                      columns=tmp_columns, max_value=tmp_max_value,
                                                                      min_value=tmp_min_value,
                                                                      max_length=tmp_max_length,
                                                                      question_open_type=tmp_question_open_type,
                                                                      validation_message=tmp_validation_message,
                                                                      size=tmp_size,
                                                                      prefix_label_object_list=tmp_prefix_label_object_list,
                                                                      postfix_label_object_list=tmp_postfix_label_object_list,
                                                                      question_header_objects_list=tmp_question_open_question_header_objects_list)

        return tmp_question_open_object

    else:
        return None


def get_answer_option_object_from_answer_option_source_object(ao_source_object, question_uid_value, page_uid_value,
                                                              var_name_string,
                                                              ao_index_value, response_domain_uid):
    tmp_uid = get_question_attribute_value_or_raise_error(source_object=ao_source_object,
                                                          attribute_string='uid',
                                                          outer_uid_value=question_uid_value,
                                                          page_uid_value=page_uid_value,
                                                          index_value=ao_index_value)

    tmp_ao_value = get_question_attribute_value_or_return_none(source_object=ao_source_object,
                                                               attribute_string='value',
                                                               outer_uid_value=question_uid_value,
                                                               page_uid_value=page_uid_value,
                                                               index_value=ao_index_value)

    if tmp_ao_value is not None:
        tmp_ao_value = int(tmp_ao_value)

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

    tmp_exclusive = get_question_attribute_value_or_return_none(source_object=ao_source_object,
                                                                attribute_string='exclusive',
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

    if tmp_exclusive is not None:
        if tmp_exclusive.lower() == "true":
            tmp_exclusive_bool = True
        else:
            tmp_exclusive_bool = False
    else:
        tmp_exclusive_bool = False

    tmp_condition = get_question_attribute_value_or_return_none(source_object=ao_source_object,
                                                                attribute_string='visible',
                                                                outer_uid_value=question_uid_value,
                                                                page_uid_value=page_uid_value,
                                                                index_value=ao_index_value)
    tmp_attached_open_object = get_question_child_or_return_none(ao_source_object, 'questionOpen')
    if tmp_attached_open_object is not None:
        tmp_attached_open = extract_question_open_object_from_source_object_or_return_none(
            source_object=tmp_attached_open_object,
            page_uid_value=page_uid_value,
            index_value=None,
            outer_uid_value=question_uid_value)
    else:
        tmp_attached_open = None

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
                                                                        attached_open=tmp_attached_open,
                                                                        exclusive_bool=tmp_exclusive_bool)
    return tmp_answer_option_object


def get_question_answer_options_objects_unit_objects_list(question_source_object, page_uid_value,
                                                          question_uid_value):
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

    tmp_response_domain_type = get_question_attribute_value_or_return_none(source_object=tmp_response_domain_object,
                                                                           attribute_string='type',
                                                                           index_value=None,
                                                                           outer_uid_value=question_uid_value,
                                                                           page_uid_value=page_uid_value)

    tmp_var_name_string = get_question_attribute_value_or_return_none(source_object=tmp_response_domain_object,
                                                                      attribute_string='variable',
                                                                      index_value=None,
                                                                      outer_uid_value=question_uid_value,
                                                                      page_uid_value=page_uid_value)

    # first iteration: find units,
    tmp_unit_objects_list = get_unit_objects_list_from_response_domain_object(
        response_domain_object=tmp_response_domain_object,
        response_domain_uid=tmp_response_domain_uid,
        page_uid_value=page_uid_value)

    tmp_unit_objects_dict = {}
    if tmp_unit_objects_list is not None:

        for uid_val, unit_object in [(i.uid, i) for i in tmp_unit_objects_list]:
            tmp_unit_objects_dict[uid_val] = unit_object

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
            for unit_ao_source_object in ao_source_object.iterchildren():
                if get_tag_from_page_children_object(unit_ao_source_object) == 'header':
                    continue

                if tmp_var_name_string is None:
                    tmp_var_name_string = get_question_attribute_value_or_raise_error(
                        source_object=unit_ao_source_object,
                        attribute_string='variable',
                        outer_uid_value=tmp_unit_uid,
                        page_uid_value=page_uid_value,
                        index_value=tmp_ao_index)

                tmp_answer_option_object = get_answer_option_object_from_answer_option_source_object(
                    ao_source_object=unit_ao_source_object,
                    question_uid_value=question_uid_value,
                    page_uid_value=page_uid_value,
                    var_name_string=tmp_var_name_string,
                    ao_index_value=tmp_ao_index,
                    response_domain_uid=tmp_response_domain_uid)
                tmp_answer_option_object.unit_object = tmp_unit_objects_dict[tmp_unit_uid]
                tmp_answer_options_list.append(tmp_answer_option_object)

        # if regular ANSWER OPTION found
        elif tmp_ao_source_object_tag == 'answerOption':
            if tmp_var_name_string is None:
                tmp_var_name_string = get_question_attribute_value_or_raise_error(
                    source_object=ao_source_object,
                    attribute_string='variable',
                    outer_uid_value=tmp_response_domain_uid,
                    page_uid_value=page_uid_value,
                    index_value=tmp_ao_index)
            tmp_answer_option_object = get_answer_option_object_from_answer_option_source_object(
                ao_source_object=ao_source_object,
                question_uid_value=question_uid_value,
                page_uid_value=page_uid_value,
                var_name_string=tmp_var_name_string,
                ao_index_value=tmp_ao_index,
                response_domain_uid=tmp_response_domain_uid)
            tmp_answer_options_list.append(tmp_answer_option_object)

        # if tag not recognized
        else:
            raise ValueError(
                'Object not recognized: uid "{0}", tag "{1}", response domain uid "{2}" on page "{3}"'.format(
                    tmp_ao_source_object_uid, tmp_ao_source_object_tag, tmp_response_domain_uid, page_uid_value))

        # tmp_answer_options_list.append(tmp_answer_option_object)
        tmp_ao_index += 1

    return tmp_answer_options_list, tmp_unit_objects_list, tmp_response_domain_type
