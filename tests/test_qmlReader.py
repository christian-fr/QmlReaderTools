# import unittest
from unittest import TestCase

from tests.context.context_graphs import \
    input_qml_01_test_file, \
    questionnaire_variables_str, \
    questionnaire_digraph_edges_str, \
    questionnaire_pages_list
from tempfile import TemporaryDirectory
from pathlib import Path


path_here = Path(__file__).parent




class TestQmlReader(TestCase):
    def setUp(self) -> None:
        # setting up the temporary directory
        self.tmp_dir = TemporaryDirectory()
        # instantiating the QmlLoader class
        self.qml_reader = qrt.util.qmlReader.QmlReader(file=input_qml_01_test_file)
        print()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()
        del self.qml_reader


    def test_read_qml_into_questionnaire(self):
        # check if all variables have been loaded correctly
        assert str(self.qml_reader.questionnaire.variables) == questionnaire_variables_str
        # check if all pages have been loaded correctly
        assert self.qml_reader.questionnaire.pages.list_of_all_pagenames() == questionnaire_pages_list
        # check if all edges have been loaded correctly
        assert str(self.qml_reader.questionnaire.DiGraph.edges) == questionnaire_digraph_edges_str

    #################

    def test_list_of_variables_from_pages(self):
        self.fail()

    def test_list_of_pages(self):
        self.fail()

    def test_startup_logger(self):
        self.fail()

    def test_set_title(self):
        self.fail()

    def test_extract_title(self):
        self.fail()

    def test_extract_variables_from_pages_body(self):
        self.fail()

    def test_return_list_of_shown_variables_in_objectified_element_descendants(self):
        self.fail()

    def test_extract_variables_from_pages_triggers(self):
        self.fail()

    def test_extract_declared_variables(self):
        self.fail()

    def test_extract_pages_to_self(self):
        self.fail()

    def test_extract_transitions_to_self(self):
        self.fail()

    def test_extract_transitions_from_qml_page_source(self):
        self.fail()

    def test_extract_questions_from_pages(self):
        self.fail()

    def test_extract_headers_and_questions_from_pages(self):
        self.fail()

    def test_extract_page_headers_from_qml_page_source(self):
        self.fail()

    def test_extract_question_objects_from_qml_page_source(self):
        self.fail()

    def test_find_tag_in_descendants(self):
        self.fail()

    def test_find_attribute_in_descendants(self):
        self.fail()

    def test_find_question_type_class_to_tag_string(self):
        self.fail()

    def test_extract_response_domains_from_question(self):
        self.fail()

    def test_extract_items_from_response_domain(self):
        self.fail()

    def test_extract_answeroptions_from_response_domain(self):
        self.fail()

    def test_extract_sources_from_questionnaire(self):
        self.fail()

    def test_extract_triggers_from_pages(self):
        self.fail()

    def test_extract_question_from_qml_page(self):
        self.fail()

    def test_extract_triggers_from_qml_page(self):
        self.fail()

    def test_extract_question_header_from_qml_element_source(self):
        self.fail()
