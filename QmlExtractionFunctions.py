__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.0.1"
__status__ = "Prototype"
__name__ = "QmlExtractionFunctions"

import QuestionnaireElements

def return_tag_from_page_children_object(page_children_object):
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


def get_question_header_objects_list(question_object):
    if hasattr(question_object, 'header'):
        for source_object in question_object.header.iterchildren():
            tmp_tag = return_tag_from_page_children_object(source_object)
            tmp_uid = get_uid_attrib_of_source_object(source_object)
            tmp_text = get_text_string_of_source_object(source_object)
            tmp_condition = get_condition_string_of_source_object(source_object)
            pass
        return []
    else:
        return []