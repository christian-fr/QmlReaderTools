import codebook.codebook as cb
import QmlReader
import QuestionnaireElements


def generate_codebook_text_element(input_string, formatting=None):
    return cb.CodebookTextElement(text_value=input_string, formatting=formatting)


def generate_codebook_text_element_with_footnote(input_string, formatting=None, footnote_string=None):
    return cb.CodebookTextElementCanHaveFootnote(text_value=input_string, formatting=formatting,
                                                 footnote_string=footnote_string)


xml_file = r'qml/questionnaire.xml'
# xml_file = r'data/questionnaire.xml'
x = QmlReader.QmlReader(xml_file)

survey_title = x.questionnaire.title

cb1 = cb.Codebook(qml_filename=xml_file, survey_title_string=survey_title)

test_counter = 0
for key, page in x.questionnaire.pages_dict.items():
    for page_object in page.page_body_objects_dict.values():
        print(page.uid)
        tmp_variables_list = []
        tmp_unit_dict = {}
        tmp_list_of_nonmissing_aos = []
        tmp_list_of_missing_aos = []

        if isinstance(page_object, QuestionnaireElements.QuestionSingleChoiceObject):
            for ao_uid, answer_option_object in page_object.answer_option_dict.items():
                # tmp_list_of_ao_dicts.append(
                #     {'uid': ao_uid, 'value': answer_option_object.value, 'label_text': answer_option_object.label_text,
                #      'unit': answer_option_object.unit_object})
                # if answer_option_object.unit_object is not None:
                #     if answer_option_object.unit_object.uid not in tmp_unit_dict.keys():
                #         tmp_unit_dict[answer_option_object.unit_object.uid] = answer_option_object.unit_object
                if answer_option_object.var_name not in tmp_variables_list:
                    tmp_variables_list.append(answer_option_object.var_name)
                # pass
                pass
                if not answer_option_object.missing_flag:
                    tmp_list_of_nonmissing_aos.append(answer_option_object)
                else:
                    tmp_list_of_missing_aos.append(answer_option_object)
            pass

            if len(tmp_variables_list) > 1:
                raise ValueError('Too many variables specified: QuestionSingleChoice, page "{0}"'.format(page.uid))
            tmp_cb_new_page = cb.CodebookPage(variable_name=tmp_variables_list[0])

            for uid, page_header_object in page.page_headers_dict.items():
                if page_header_object.text is not None:
                    tmp_page_header_text_object_string = page_header_object.text
                    tmp_page_header_text_object_condition = str(page_header_object.condition)
                    tmp_page_header_text_object_formatting = None

                    if page_header_object.page_header_type == 'title':
                        tmp_page_header_text_object_formatting = 'textbf'

                    if tmp_page_header_text_object_condition.lower() != 'true':
                        tmp_page_header_text_object = cb.CodebookTextElementCanHaveFootnote(text_value=tmp_page_header_text_object_string, formatting=tmp_page_header_text_object_formatting, footnote_string=tmp_page_header_text_object_condition)
                        tmp_cb_new_page.add_object(tmp_page_header_text_object)
                    else:
                        tmp_page_header_text_object = cb.CodebookTextElement(
                            text_value=tmp_page_header_text_object_string,
                            formatting=tmp_page_header_text_object_formatting)

            for uid, question_header_object in page_object.question_header_dict.items():
                tmp_question_header_text_object_string = question_header_object.text
                tmp_question_header_text_object_condition = str(question_header_object.condition)
                tmp_question_header_text_object_formatting = None

                if question_header_object.header_type == 'question':
                    tmp_question_header_text_object_formatting = 'textbf'
                if question_header_object.header_type == 'instruction':
                    tmp_question_header_text_object_formatting = 'textit'

                if tmp_question_header_text_object_condition.lower() != 'true':
                    tmp_question_header_text_object = cb.CodebookTextElementCanHaveFootnote(
                        text_value=tmp_question_header_text_object_string, formatting=tmp_question_header_text_object_formatting,
                        footnote_string=tmp_question_header_text_object_condition)
                    tmp_question_header_text_object.generate_latex_code_output()
                    tmp_question_header_text_object.add_footnote_to_latex_code()
                else:
                    tmp_question_header_text_object = cb.CodebookTextElement(
                        text_value=tmp_question_header_text_object_string,
                        formatting=tmp_question_header_text_object_formatting)
                    tmp_question_header_text_object.generate_latex_code_output()
                tmp_cb_new_page.add_object(tmp_question_header_text_object)

            for answer_option_object in tmp_list_of_nonmissing_aos:
                if answer_option_object.label_text is None:
                    tmp_label_string = str(answer_option_object.value) + ' [no label]'
                else:
                    tmp_label_string = str(answer_option_object.value) + ' ' + answer_option_object.label_text
                tmp_condition_string = str(answer_option_object.condition)
                if tmp_condition_string.lower() != 'true':
                    tmp_cb_text_element = generate_codebook_text_element_with_footnote(input_string=tmp_label_string,
                                                                                       footnote_string=tmp_condition_string)
                else:
                    tmp_cb_text_element = generate_codebook_text_element(input_string=tmp_label_string)
                tmp_cb_new_page.add_object(tmp_cb_text_element)

            if tmp_list_of_missing_aos:
                tmp_cb_new_page.add_object(cb.CodebookTextElement(text_value='.'))

            for answer_option_object in tmp_list_of_missing_aos:
                tmp_label_string = str(answer_option_object.value) + ' ' + answer_option_object.label_text
                tmp_condition_string = str(answer_option_object.condition)
                if tmp_condition_string.lower() != 'true':
                    tmp_cb_text_element = generate_codebook_text_element_with_footnote(input_string=tmp_label_string, formatting='textit',
                                                                                       footnote_string=tmp_condition_string)
                else:
                    tmp_cb_text_element = generate_codebook_text_element(input_string=tmp_label_string, formatting='textit')
                tmp_cb_new_page.add_object(tmp_cb_text_element)


            cb1.add_codebook_page(tmp_cb_new_page)


    test_counter += 1

cb1.generate_latex_code()
cb1.write_latex_file()
