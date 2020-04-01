__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.5"
__status__ = "Prototype"
__name__ = "QmlReader"
# last edited: 2020-04-01

from os import path, sys
from lxml import etree, objectify
import io
import copy
import networkx as nx
import re

if sys.platform is not 'win32':
    import pygraphviz as pgv
from Questionnaire import QmlPage, Questionnaire


class QmlReader:
    """
    Class for Reading and extracting elements from QML-Files.

    self.dict_of_page_numbers:
        dictionary of: {lfdNr: 'pageNr/Uid'}

    self.dict_of_page_numbers_reversed:
        dictionary of: {'pageNr/Uid': lfdNr}

    """

    def __init__(self, file, create_graph=False, draw=False, truncate=False):
        self.pages_variables = {}
        self.DiGraph = nx.DiGraph()
        self.dict_of_transitions = {}
        self.dict_of_sources = {}
        self.sourcepath = path.split(file)[0]
        self.sourcefullfilename = path.split(file)[1]
        self.sourcefilename = path.splitext(self.sourcefullfilename)[0]
        with open(file, 'rb') as f:
            self.data = f.read()

        self.root = objectify.fromstring(self.data)
        self.Variables = []
        self.title = 'Survey'
        self.set_title()
        self.dict_of_page_numbers = self.extract_page_numbers()
        self.dict_of_page_numbers_reversed = {v: k for k, v in self.dict_of_page_numbers.items()}
        self.extract_transitions()
        self.extract_sources()
        self.variables_from_declaration = self.extract_variables_from_declaration()
        self.variables_from_pages = self.extract_variables_from_pages()
        self.replace_conditions()
        self.extract_data()
        if truncate:
            self.dict_of_transitions_truncated = copy.deepcopy(self.dict_of_transitions)
            self.truncate_data()

        self.__init_my_own_graph()
        self.__add_pages_to_my_graph_from_data()
        if sys.platform is not 'win32':
            if create_graph:
                self.transitions_to_nodes_edges(truncate=False)
                self.init_pgv_graph()
                if draw:
                    nx.write_gml(self.DiGraph, self.sourcepath + '/' + self.sourcefilename + '.gml')
                    self.draw_pgv_graph(self.sourcepath + '/' + self.sourcefilename + '.png')

    def list_of_unused_variables(self):
        return list(set(self.list_of_variables_from_declaration()).difference(self.list_of_variables_from_pages()))

    def list_of_pages(self):
        return list(self.dict_of_page_numbers_reversed.keys())

    def list_of_variables_from_declaration(self):
        l = []
        for i in self.variables_from_declaration:
            l.append(list(i.keys())[0])
        return l

    def list_of_variables_from_pages(self):
        l = []
        for key in self.pages_variables.keys():
            for item in self.pages_variables[key]:
                l.append(item)
        return l

    def list_of_variables_on_page(self, pagename="index"):
        if pagename in self.pages_variables.keys():
            return self.pages_variables[pagename]
        else:
            return ['page not found']

    def find_page_from_variable(self, variablename="width"):
        """
        :param variablename:
        input: name of the variable that has to be found

        :return:
        list of pages where this variable is used
        """
        key_liste = []
        for key in self.pages_variables.keys():
            if variablename in self.pages_variables[key]:
                key_liste.append(key)
        if len(key_liste) is not 0:
            return key_liste
        else:
            return ['variable not found']

    def replace_conditions(self):
        regex1 = re.compile(r'\s+')
        regex2 = re.compile(r'zofar\.asNumber\(([a-z0-9A-Z_\-]+)\)')
        regex3 = re.compile(r'==([0-9])')
        regex4a = re.compile(r'!zofar\.isMissing\(([a-z0-9A-Z\-_]+)\)')
        regex4b = re.compile(r'zofar\.isMissing\(([a-z0-9A-Z\-_]+)\)')
        regex5 = re.compile(r'!([a-z0-9A-Z\-_]+)\.value')
        regex6 = re.compile(r'([a-z0-9A-Z\-_]+)\.value')
        regex7 = re.compile(r' and ')
        regex8 = re.compile(r' or ')
        regex9 = re.compile(r'PRELOAD')
        regex10 = re.compile(r'dropDown')
        regex11 = re.compile(r'replace.*[^ ]$')
        regex12 = re.compile(r'\&')
        regex13 = re.compile(r'\|')

        for i in self.dict_of_transitions.keys():
            for k in self.dict_of_transitions[i].keys():
                if self.dict_of_transitions[i][k]['condition'] is not None:
                    self.dict_of_transitions[i][k]['condition_new'] = regex1.sub(' ', self.dict_of_transitions[i][k][
                        'condition'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex2.sub(r'\g<1> ',
                                                                                 self.dict_of_transitions[i][k][
                                                                                     'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex3.sub(r'== \g<1>',
                                                                                 self.dict_of_transitions[i][k][
                                                                                     'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex4a.sub(r'\g<1> != MISS',
                                                                                  self.dict_of_transitions[i][k][
                                                                                      'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex4b.sub(r'\g<1> == MISS',
                                                                                  self.dict_of_transitions[i][k][
                                                                                      'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex5.sub(r'\g<1> != 1',
                                                                                 self.dict_of_transitions[i][k][
                                                                                     'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex6.sub(r'\g<1> == 1',
                                                                                 self.dict_of_transitions[i][k][
                                                                                     'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex7.sub(r' & ', self.dict_of_transitions[i][k][
                        'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex8.sub(r' | ', self.dict_of_transitions[i][k][
                        'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex9.sub(r'', self.dict_of_transitions[i][k][
                        'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex10.sub(r'', self.dict_of_transitions[i][k][
                        'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex12.sub(r'& \n',
                                                                                  self.dict_of_transitions[i][k][
                                                                                      'condition_new'])
                    self.dict_of_transitions[i][k]['condition_new'] = regex13.sub(r'| \n',
                                                                                  self.dict_of_transitions[i][k][
                                                                                      'condition_new'])

    def transitions_to_nodes_edges(self, truncate=False):
        if truncate:
            # self.DiGraph.add_nodes_from(list(self.dict_of_page_numbers_reversed.keys()))
            for i in self.dict_of_page_numbers_reversed.keys():
                self.DiGraph.add_node(i, label=i + '\n' + '\n'.join(self.pages_variables[i]))
            dict_transitions = {}
            for i in self.dict_of_transitions_truncated.keys():
                cnt = 0
                for k in self.dict_of_transitions_truncated[i].keys():

                    if self.dict_of_transitions_truncated[i][k]['condition'] is not None:
                        if tuple([i, self.dict_of_transitions_truncated[i][k]['target']]) in dict_transitions.keys():
                            dict_transitions[tuple([i, self.dict_of_transitions_truncated[i][k]['target']])] = \
                            dict_transitions[
                                tuple([i,
                                       self.dict_of_transitions_truncated[
                                           i][
                                           k][
                                           'target']])] + ' |\n(' + '[' + str(
                                cnt) + '] ' + self.dict_of_transitions_truncated[i][k]['condition_new'] + ')'
                            self.DiGraph.add_edge(i, self.dict_of_transitions_truncated[i][k]['target'],
                                                  label='[' + str(cnt) + '] ' + dict_transitions[
                                                      tuple([i, self.dict_of_transitions_truncated[i][k]['target']])])
                        else:
                            dict_transitions[tuple([i, self.dict_of_transitions_truncated[i][k]['target']])] = '(' + \
                                                                                                               '[' + str(
                                cnt) + '] ' + \
                                                                                                               self.dict_of_transitions_truncated[
                                                                                                                   i][
                                                                                                                   k][
                                                                                                                   'condition_new'] + ')'
                        self.DiGraph.add_edge(i, self.dict_of_transitions_truncated[i][k]['target'],
                                              label=dict_transitions[
                                                  tuple([i, self.dict_of_transitions_truncated[i][k]['target']])])
                        cnt = cnt + 1

                    else:
                        if tuple([i, self.dict_of_transitions_truncated[i][k]['target']]) in dict_transitions.keys():
                            self.DiGraph.add_edge(i, self.dict_of_transitions_truncated[i][k]['target'],
                                                  label='')
                        else:
                            if cnt is 0:
                                self.DiGraph.add_edge(i, self.dict_of_transitions_truncated[i][k]['target'],
                                                      label='')
                            if cnt is not 0:
                                self.DiGraph.add_edge(i, self.dict_of_transitions_truncated[i][k]['target'],
                                                      label='[' + str(cnt) + ']')

                        cnt += 1

        else:

            for i in self.dict_of_page_numbers_reversed.keys():
                self.DiGraph.add_node(i, label=i + '\n' + '\n'.join(self.pages_variables[i]))
            dict_transitions = {}
            for i in self.dict_of_transitions.keys():
                cnt = 0
                for k in self.dict_of_transitions[i].keys():

                    if self.dict_of_transitions[i][k]['condition'] is not None:
                        if tuple([i, self.dict_of_transitions[i][k]['target']]) in dict_transitions.keys():
                            dict_transitions[tuple([i, self.dict_of_transitions[i][k]['target']])] = dict_transitions[
                                                                                                         tuple([i,
                                                                                                                self.dict_of_transitions[
                                                                                                                    i][
                                                                                                                    k][
                                                                                                                    'target']])] + ' |\n(' + '[' + str(
                                cnt) + '] ' + self.dict_of_transitions[i][k]['condition_new'] + ')'
                            self.DiGraph.add_edge(i, self.dict_of_transitions[i][k]['target'],
                                                  label='[' + str(cnt) + '] ' + dict_transitions[
                                                      tuple([i, self.dict_of_transitions[i][k]['target']])])
                        else:
                            dict_transitions[tuple([i, self.dict_of_transitions[i][k]['target']])] = '(' + \
                                                                                                     '[' + str(
                                cnt) + '] ' + \
                                                                                                     self.dict_of_transitions[
                                                                                                         i][k][
                                                                                                         'condition_new'] + ')'
                        self.DiGraph.add_edge(i, self.dict_of_transitions[i][k]['target'],
                                              label=dict_transitions[
                                                  tuple([i, self.dict_of_transitions[i][k]['target']])])
                        cnt = cnt + 1

                    else:
                        if tuple([i, self.dict_of_transitions[i][k]['target']]) in dict_transitions.keys():
                            self.DiGraph.add_edge(i, self.dict_of_transitions[i][k]['target'],
                                                  label='')
                        else:
                            if cnt is 0:
                                self.DiGraph.add_edge(i, self.dict_of_transitions[i][k]['target'],
                                                      label='')
                            if cnt is not 0:
                                self.DiGraph.add_edge(i, self.dict_of_transitions[i][k]['target'],
                                                      label='[' + str(cnt) + ']')

                        cnt += 1

        self.init_pgv_graph()

    def init_pgv_graph(self, graph_name='graph'):
        self.pgv_graph = nx.nx_agraph.to_agraph(self.DiGraph)

        self.pgv_graph.node_attr['shape'] = 'box'
        self.pgv_graph.graph_attr['label'] = 'title: ' + self.title + '\nfile: ' + self.sourcefilename
        self.pgv_graph.layout("dot")

    def draw_pgv_graph(self, output_file='output_file.png'):
        self.pgv_graph.draw(output_file)

    def extract_transitions(self):
        for i in self.dict_of_page_numbers:
            self.dict_of_transitions[self.dict_of_page_numbers[i]] = {}
            # print("i")
            # print(i)
            flag_transitions = False
            try:
                x = len(self.root.page[i].transitions.transition)
                flag_transitions = True
            except:
                pass

            if flag_transitions:
                for t in range(0, len(self.root.page[i].transitions.transition)):
                    self.dict_of_transitions[self.dict_of_page_numbers[i]][t] = ''

                    try:
                        self.dict_of_transitions[self.dict_of_page_numbers[i]][t] = {
                            'target': self.root.page[i].transitions.transition[t].attrib['target'],
                            'condition': self.root.page[i].transitions.transition[t].attrib['condition']}
                    except KeyError:
                        self.dict_of_transitions[self.dict_of_page_numbers[i]][t] = {
                            'target': self.root.page[i].transitions.transition[t].attrib['target'],
                            'condition': None}

    def extract_page_numbers(self):
        dict_of_page_numbers = {}
        for i in range(0, len(self.root.page)):
            dict_of_page_numbers[i] = self.root.page[i].attrib['uid']
        return dict_of_page_numbers

    @staticmethod
    def write2file(path, list_of_strings):
        # if isinstance(list_of_strings,ValueError: Unicode strings with encoding declaration are not supported.
        # Please use bytes input or XML fragments without declaration.b list):
        try:
            assert isinstance(list_of_strings, list) == True
            outfile = io.open(path, 'w', encoding='cp1252')
            for string in list_of_strings:
                outfile.write(string.decode("utf-8") + "\n")
            outfile.close()
            print('Successfully written ' + str(len(list_of_strings)) + ' lines to file: ' + path)
        except AssertionError as error:
            print('error')
            print('The data passed to the object was not of type: list.')

    def extract_data(self, use_variables=True, use_pagenames=True, labels=True):
        for pagenr in range(0, len(self.root.page)):
            list_variables_per_page = []
            if use_variables:
                if hasattr(self.root.page[pagenr], 'body'):
                    for i in self.root.page[pagenr].body.iterdescendants():
                        try:
                            list_variables_per_page.append(i.attrib['variable'])
                        except:
                            pass
            self.pages_variables[self.root.page[pagenr].attrib["uid"]] = list_variables_per_page

    def set_title(self, title='Survey'):
        self.title = self.extract_title()

    def extract_variables_from_declaration(self):
        results_list = []
        for i in range(0, len(self.root.variables.variable)):
            temp_dict = {self.root.variables.variable[i].attrib["name"]: self.root.variables.variable[i].attrib["type"]}
            results_list.append(temp_dict)

        self.Variables = results_list
        return results_list

    @staticmethod
    def list_of_dicts_to_list_of_csv(input_list):
        results_list = []
        for dictionary in input_list:
            temp_string = ""
            counter = 0
            for key in dictionary:
                temp_string = temp_string + str(key) + str(dictionary[key])
                if counter < len(dictionary):
                    temp_string = temp_string + ", "
                counter = counter + 1
                results_list.append(temp_string)
        return results_list

    def __init_my_own_graph(self):
        self.Questionnaire = Questionnaire()

    def __add_pages_to_my_graph_from_data(self):
        __newpage = None
        for pagename in self.dict_of_page_numbers_reversed.keys():
            __newpage = QmlPage(pagename)
            __newpage.add_transition(self.dict_of_transitions[pagename])
            self.Questionnaire.add_page(__newpage)

    def extract_variables_from_pages(self):
        ao_list = []
        for k in range(0, 100):
            ao_list.append('ao' + str(k))

        results_dict = {}
        for i in range(0, len(self.root.page)):
            if hasattr(self.root.page[i], 'body'):
                for child in self.root.page[i].body.iterdescendants():
                    if 'responseDomain' in child.tag and 'variable' in child.attrib:
                        results_dict[child.attrib['variable']] = {'values': [], 'page': self.dict_of_page_numbers[i]}
                        for grandchild in child.iterdescendants():
                            if 'uid' in grandchild.attrib:
                                if grandchild.attrib['uid'] in ao_list and 'value' in grandchild.attrib:
                                    results_dict[child.attrib['variable']]['values'].append(grandchild.attrib['value'])
                                    if 'label' in grandchild.attrib:
                                        results_dict[child.attrib['variable']]['label'] = grandchild.attrib['label']
                    elif 'answerOption' in child.tag and 'value' not in child.attrib and 'label' in child.attrib:
                        results_dict[child.attrib['variable']] = {'values': [True, False],
                                                                  'page': self.dict_of_page_numbers[i],
                                                                  'label': child.attrib['label']}
                    elif 'questionOpen' in child.tag and 'variable' in child.attrib:
                        if child.attrib['variable'] not in results_dict:
                            results_dict[child.attrib['variable']] = {'type': 'string', 'values': [],
                                                                      'answer_options': None,
                                                                      'page': self.dict_of_page_numbers[i]}
            else:
                pass
        return results_dict

    def extract_title(self):
        return self.root.name.text

    def extract_sources(self):
        self.dict_of_sources = {}
        for key in self.dict_of_transitions:
            self.dict_of_sources[key] = []

        # input: dict of transitions
        for key in self.dict_of_transitions:
            for num in self.dict_of_transitions[key]:
                target = self.dict_of_transitions[key][num]['target']
                self.dict_of_sources[target].append(key)

        for key in self.dict_of_sources:
            tmp_dict = {}
            self.dict_of_sources[key] = list(set(self.dict_of_sources[key]))
            for entry in self.dict_of_sources[key]:
                if len(self.dict_of_transitions[entry]) is 1:
                    tmp_dict[entry] = {'single_transition': True}
                else:
                    tmp_dict[entry] = {'single_transition': False}
            self.dict_of_sources[key] = tmp_dict

    def truncate_data(self):
        list_of_pages = self.check_for_pages_to_truncate()
        self.change_labels_and_delete_pages_to_truncate(list_of_pages)

    def change_labels_and_delete_pages_to_truncate(self, list_of_pages):
        return
        list_done = []
        for i in range(0, len(list_of_pages) - 1):
            page = list_of_pages[i]
            next_page = list_of_pages[i + 1]
            sucessor = self.dict_of_transitions[page][0]['target']
            temp_str = ''
            cnt = 0
            if page in list_done:
                continueX

            while True:
                cnt += 1
                if next_page is sucessor:
                    if temp_str is '':
                        temp_str = page
                    else:
                        temp_str = temp_str + ',' + page
                    list_done.append(page)
                else:
                    print('page:' + str(page))
                    print('i:' + str(i))
                    print('next_page:' + str(next_page))
                    print('temp_str:' + str(temp_str))
                    self.dict_of_transitions_truncated[list(self.dict_of_sources[list_of_pages[i]].keys())[0]][0][
                        'condition'] = temp_str
                    break

                if i + cnt + 1 < len(list_of_pages):
                    page = list_of_pages[i + cnt]
                    next_page = list_of_pages[i + cnt + 1]
                    sucessor = self.dict_of_transitions[page][0]['target']

                else:
                    self.dict_of_transitions_truncated[list(self.dict_of_sources[list_of_pages[i]].keys())[0]][0][
                        'condition'] = temp_str
                    break
            self.dict_of_transitions_truncated.pop(list_of_pages[i])

    def check_for_pages_to_truncate(self):
        list_of_pages = []
        for page in self.dict_of_page_numbers_reversed:
            if page in self.dict_of_sources and page in self.dict_of_transitions:
                if page is not 'index' and page is not 'end' and len(self.dict_of_sources[page].keys()) is 1 and len(
                        self.dict_of_transitions[page]) is 1:
                    predecessor = list(self.dict_of_sources[page].keys())[0]
                    successor = self.dict_of_transitions[page][0]['target']
                    if len(self.dict_of_sources[predecessor].keys()) is 1 and len(
                            self.dict_of_transitions[successor]) is 1:
                        list_of_pages.append(page)
                        # predecessor = list(self.dict_of_sources[page].keys())[0]
        return list_of_pages
