__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "MIT"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "advancedFlowchart"

import os
import pandas as pd
import pygraphviz
from math import ceil
import matplotlib as mpl
import numpy as np


def check_if_two_consecutive_entries_in_list_of_lists(entry1, entry2, input_list):
    tmp_list_of_all_tuples = []
    if (entry1, entry2) in [item for elem in [list(zip(i, i[1:])) for i in input_list] for item in elem]:
        return True
    else:
        return False


def invert_arrowheads(graph):
    """
    Changes the arrowheads of the graph to inverted arrowheads.
    :param graph: a pygraphviz agraph
    :return: None
    """
    for edge in graph.edges():
        edge.attr['arrowhead'] = 'inv'


def create_dict_of_weights_from_data(input_list, edges=True):
    dict_of_weights = {}
    if edges:  # for edges lists
        assert isinstance(input_list, list)
        assert list(set([isinstance(i, tuple) for i in input_list]))[0]
        pass
    else:  # for nodes lists
        pass
    return dict_of_weights


def create_stack_list(input_list):
    """
    Does tw
    :param input_list: list (of page visits), duplicates are possible
    :return: tuple(stack list, list_of_backwards_jumps): stack_list is very similar to the input list, but without loops
        and consecutive duplicates; list_of_backwards_jumps is a list of tuples of all backwards jumps that have been
        made.
    """
    stack_list = []
    list_of_backward_jumps = []

    for i in range(0, len(input_list)):
        if i > 0 and input_list[i] == input_list[i - 1]:
            continue

        if input_list[i] not in stack_list:
            stack_list.append(input_list[i])
        else:
            list_of_backward_jumps.append((stack_list.pop(), input_list[i]))
    if 'end' in input_list:
        print('sprünge nach "end":')
        print(input_list[input_list.index('end'):])

    list_of_returning_points = [i for i in filter(None, [set(i) - set(stack_list) for i in
                                                         input_list])]  # identifies the nodes that do appear in the input, but not in the stack list
    # [i for i in filter(None, list_of_returning_points)]

    return stack_list, list_of_backward_jumps, list_of_returning_points


def create_blue_red_color_gradient_list(steps=256):
    """
    :param steps:
    :return: list of color values
    """

    c1 = 'blue'
    c2 = 'red'
    n = steps

    color_gradient_list = [color_fader(c1, c2, i / n) for i in range(0, n)]
    return color_gradient_list


def color_fader(c1, c2, mix=0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    """
    :param c2:
    :param c1:
    :type mix: float
    """
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)


class AdvancedFlowchart:
    def __init__(self, digraph, pandas_dataset, input_graph):
        self.dataset_path = None
        self._set_dataset_path(pandas_dataset)

        self.history_dataset = None
        self.history_as_list = []
        self._read_dataset()

        self._colorfader = create_blue_red_color_gradient_list(256)

        self.input_graph_path = None
        self._set_input_graph_path(input_graph)
        self._input_graph = None
        self._read_input_graph()

        self.graphs = []

        self.create_trail_of_effective_edges()
        self.create_trail_of_backwards_jumps()
        self.create_highlight_points_of_return()

    def _set_dataset_path(self, pandas_dataset):
        assert os.path.isfile(pandas_dataset)
        self.dataset_path = pandas_dataset

    def create_trail(self, graph, dict_of_weights_of_edges, colorfader_list, max_line_width=10, backwards=False):
        """
        :type dict_of_weights_of_edges: dict
        :param backwards: toggles reversing of edge order (source <--> target) for backwards jumps (so that they can be
            found in the forward directed graph)
        :param max_line_width: max penwidth of line
        :param colorfader_list: list of hex colors
        :param graph: input graph, DiGraph form networkx
        :param dict_of_weights_of_edges: dictionary of weights
        :return: tuple of two lists: list of used edges from graph, list of unused edges from graph
        """
        assert isinstance(graph, pygraphviz.agraph.AGraph)
        assert isinstance(dict_of_weights_of_edges, dict)
        list_of_used_edges_tuples = []
        list_of_unused_edges_tuples = []
        tmp_edge = ()
        for edge in graph.edges():
            if backwards:
                tmp_edge = (edge[1], edge[0])
            else:
                tmp_edge = edge
            if tmp_edge in dict_of_weights_of_edges.keys():
                list_of_used_edges_tuples.append(tmp_edge)

                # print('weight from dict: ' + str(dict_of_weights_of_edges[(edge[1], edge[0])]))
                edge.attr['penwidth'] = ceil(dict_of_weights_of_edges[tmp_edge] * max_line_width + 1)
                edge.attr['color'] = colorfader_list[
                    ceil(dict_of_weights_of_edges[tmp_edge] * (len(colorfader_list) - 1))]
                # print('penwidth at edge: ' + str(edge.attr['penwidth']))

            else:
                list_of_unused_edges_tuples.append(tmp_edge)
        print('edges in graph without corresponding edges in data: \n' + str(list_of_unused_edges_tuples))
        return list_of_used_edges_tuples, list_of_unused_edges_tuples

    def modify_graph(self, graph, title, dict_of_weights_of_nodes=None, dict_of_weights_of_edges=None,
                     func_for_penwidth_edges=None, func_for_colorfader_edges=None, func_for_penwidth_nodes=None,
                     func_for_colorfader_nodes=None, reverse_edges=False):
        """

        :param graph:
        :param title:
        :param dict_of_weights_of_nodes:
        :param dict_of_weights_of_edges:
        :param func_for_penwidth:
        :param func_for_colorfader:
        :return:
        """
        assert isinstance(graph, pygraphviz.agraph.AGraph)
        assert isinstance(dict_of_weights_of_nodes, dict)
        list_of_used_edges_tuples = []
        list_of_unused_edges_tuples = []
        tmp_edge = ()
        if dict_of_weights_of_edges is not None:
            for edge in graph.edges():
                if reverse_edges:
                    tmp_edge = (edge[1], edge[0])
                else:
                    tmp_edge = edge
                if tmp_edge in dict_of_weights_of_edges.keys():
                    list_of_used_edges_tuples.append(tmp_edge)
                    if func_for_penwidth_edges is not None:
                        edge.attr['penwidth'] = func_for_penwidth_edges(dict_of_weights_of_edges[tmp_edge])
                    # ceil(dict_of_weights_of_edges[tmp_edge] * max_line_width + 1)
                    if func_for_colorfader_edges is not None:
                        edge.attr['color'] = func_for_colorfader_edges(dict_of_weights_of_edges[tmp_edge])
                    # colorfader_list[ceil(dict_of_weights_of_edges[tmp_edge] * (len(colorfader_list) - 1))]
                else:
                    list_of_unused_edges_tuples.append(tmp_edge)

        list_of_used_nodes_strings = []
        list_of_unused_nodes_strings = []
        if dict_of_weights_of_nodes is not None:
            for node in graph.nodes():
                if node in dict_of_weights_of_nodes.keys():
                    list_of_used_nodes_strings.append(node)
                    if func_for_penwidth_nodes is not None:
                        node.attr['penwidth'] = func_for_penwidth_nodes(dict_of_weights_of_nodes[node])
                    # ceil(dict_of_weights_of_nodes[node] * 10 + 1)
                    if func_for_colorfader_nodes is not None:
                        node.attr['color'] = func_for_colorfader_nodes(dict_of_weights_of_edges[tmp_edge])
                    # self.colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]
                else:
                    list_of_unused_nodes_strings.append(node)

        return list_of_used_nodes_strings, list_of_unused_nodes_strings, list_of_used_edges_tuples, list_of_unused_edges_tuples

    def create_graph_highlight_points_of_return(self, graph, dict_of_weights_of_nodes):
        """

        :param graph: input graph, DiGraph form networkx
        :param dict_of_weights_of_nodes: dictionary of weights
        :return: tuple of two lists: list of used nodes from graph, list of unused nodes from graphb
        """
        assert isinstance(graph, pygraphviz.agraph.AGraph)
        assert isinstance(dict_of_weights_of_nodes, dict)
        list_of_used_nodes_strings = []
        list_of_unused_nodes_strings = []
        for node in graph.nodes():
            if node in dict_of_weights_of_nodes.keys():
                print(node.name)
                list_of_used_nodes_strings.append(node)
                print('weight from dict: ' + str(dict_of_weights_of_nodes[node]))
                node.attr['penwidth'] = ceil(dict_of_weights_of_nodes[node] * 10 + 1)
                print('color: ' + str(self._colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]))
                node.attr['color'] = self._colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]
                print('penwidth at node: ' + str(node.attr['penwidth']))

            else:
                list_of_unused_nodes_strings.append(node)
        print('nodes in graph without corresponding nodes in data: \n' + str(list_of_unused_nodes_strings))
        return list_of_used_nodes_strings, list_of_unused_nodes_strings

    def _read_dataset(self):
        self.history_dataset = pd.read_csv(self.dataset_path, dtype='unicode')

        for entry in list(self.history_dataset['page_history']):
            if not isinstance(entry, float):
                self.history_as_list.append(entry[2:-2].split("', '"))

    def _set_input_graph_path(self, input_graph_path):
        assert os.path.isfile(input_graph_path)
        self.dataset_path = input_graph_path

    def _read_input_graph(self):
        self._input_graph = pygraphviz.agraph.AGraph()
        self._input_graph.read(self.input_graph_path)
        self._input_graph.layout('dot')

    def create_trail_of_effective_edges(self):
        pass

    def create_highlight_points_of_return(self):
        pass
