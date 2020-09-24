def extract_variables_from_pages_body(self):
    self.logger.info("extract_variables_from_pages_body")
    for pagenr in range(0, len(self.root.page)):
        tmp_pagename = self.root.page[pagenr].attrib['uid']
        if hasattr(self.root.page[pagenr], 'body'):
            for i in self.root.page[pagenr].body.iterdescendants():
                if 'variable' in i.attrib:
                    tmp_varname = i.attrib['variable']
                    tmp_var_object = QuestionnaireElements.VariableObject(tmp_varname, var_type_string=)
                    tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(varplace='body', varname=tmp_varname)
                    if tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].variables.list_all_vars() and tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                        self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                    else:
                        self.logger.info('Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(tmp_pagename) + '". Possible duplicate.')
                        self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(tmp_var_object, replace=True)

def extract_variables_from_pages_triggers(self):
    self.logger.info("extract_variables_from_pages_triggers")
    for pagenr in range(0, len(self.root.page)):
        tmp_pagename = self.root.page[pagenr].attrib['uid']
        if hasattr(self.root.page[pagenr], 'triggers'):
            for i in self.root.page[pagenr].triggers.iterdescendants():
                try:
                    tmp_varname = i.attrib['variable']
                    tmp_var_object = self.questionnaire.variables.variables[tmp_varname].set_varplace(varplace='triggers', varname=tmp_varname)
                    if tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].variables.list_all_vars() and tmp_varname not in self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.list_all_vars():
                        self.questionnaire.pages.pages[tmp_pagename].variables.add_variable(tmp_var_object)
                    else:
                        self.logger.info('Variable "' + str(tmp_varname) + '" already in self.variables of page "' + str(tmp_pagename) + '". Possible duplicate.')
                        self.questionnaire.pages.pages[tmp_pagename].duplicate_variables.add_variable(tmp_var_object, replace=True)
                except KeyError:
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
        if len([i for i in qml_source_page.header.iterchildren()]) > 0:
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
                tmp_object = QuestionnaireObject.PageHeaderObject(uid=tmp_uid, tag=tmp_tag, text=tmp_text,
                                                                  index=tmp_index,
                                                                  visible_conditions=tmp_visible_conditions)

                self.logger.info("  adding PageHeaderObject: '" + str(tmp_object.tag) + "' to page: " + str(page_uid))
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
        tmp_body_uid = qml_source_page.body.attrib['uid']
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
                pass

            elif tmp_tag == 'multipleChoice':
                pass

            elif tmp_tag == 'questionOpen':
                pass

            elif tmp_tag == 'questionPretest':
                pass

            elif tmp_tag == 'questionSingleChoice':
                pass

                # ToDo
                ## self.questionnaire.pages.pages[page_uid].questions.add_question_object()

                (self.extract_question_header_from_qml_element_source(element, page_uid))
            if tmp_tag == 'section':
                pass

    pass


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
                self.questionnaire.pages.pages[transition.target].sources.add_source(page.question_uid)
            else:
                tmp_dict_of_additional_pages[transition.target] = page.question_uid
    # ToDo: (see above) the following is just a workaround until option "combine" is implemented issue#9
    for newpagename in tmp_dict_of_additional_pages.keys():
        self.questionnaire.pages.add_page(QuestionnaireObject.QmlPage(newpagename, declared=False))
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


def extract_question_header_from_qml_element_source(self, qml_source_element, page_uid):
    flag_question = False
    flag_instruction = False
    flag_introduction = False
    tmp_header = QuestionnaireObject.QuestionHeader()
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
                    self.logger.info(
                        '  unexpected tag found: "' + str(header_question_object.tag) + '" in header on page ' + str(
                            page_uid))
                    raise ValueError(
                        '  unexpected tag found: "' + str(header_question_object.tag) + '" in header on page ' + str(
                            page_uid))

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
                QuestionnaireObject.QuestionHeaderObject(uid=tmp_uid, text=tmp_text, tag=tmp_tag, index=tmp_index,
                                                         visible_conditions=tmp_visible))
    return tmp_header