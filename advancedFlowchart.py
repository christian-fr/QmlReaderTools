__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.1.0"
__status__ = "Prototype"
__name__ = "advancedFlowchart"


import os
import pandas as pd
import pygraphviz
from math import ceil
import matplotlib as mpl
import numpy as np


def create_color_gradient_list(steps=256):
    """

    :param steps:
    :return: list of color values
    """

    c1 = 'blue'
    c2 = 'red'
    n = steps

    color_gradient_list = [color_fader(c1, c2, i / n) for i in range(0, n)]
    return color_gradient_list


class AdvancedFlowchart:
    def __init__(self, digraph, pandas_dataset):
        self.dataset_path = None
        self.set_dataset_path(pandas_dataset)

        self.AGraph = None
        self.set_agraph(digraph)

    def set_dataset_path(self, pandas_dataset):
        assert os.path.isfile(pandas_dataset)
        self.dataset_path = pandas_dataset

    def set_agraph(self, agraph):
        assert isinstance(agraph, pygraphviz.agraph.AGraph)
        self.AGraph = agraph

    def create_trail(self, graph, dict_of_weights_of_edges, colorfader_list, max_line_width=10, backwards=False):
        """
        :param max_line_width: max penwidth of line
        :param colorfader: list of
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
                h
                # print('weigth from dict: ' + str(dict_of_weights_of_edges[(edge[1], edge[0])]))
                edge.attr['penwidth'] = ceil(dict_of_weights_of_edges[tmp_edge] * max_line_width + 1)
                edge.attr['color'] = colorfader_list[
                    ceil(dict_of_weights_of_edges[tmp_edge] * (len(colorfader_list) - 1))]
                # print('penwidth at edge: ' + str(edge.attr['penwidth']))

            else:
                list_of_unused_edges_tuples.append(tmp_edge)
        print('edges in graph without corresponding edges in data: \n' + str(list_of_unused_edges_tuples))
        return list_of_used_edges_tuples, list_of_unused_edges_tuples

    def create_highlight_points_of_return(self, graph, dict_of_weights_of_nodes):
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
                print('color: ' + str(colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]))
                node.attr['color'] = colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]
                print('penwidth at node: ' + str(node.attr['penwidth']))

            else:
                list_of_unused_nodes_strings.append(node)
        print('nodes in graph without corresponding nodes in data: \n' + str(list_of_unused_nodes_strings))
        return list_of_used_nodes_strings, list_of_unused_nodes_strings

    def read_dataset(self):
        self.data = pd.read_csv(self.dataset_path, dtype='unicode')

        history_liste = []
        for entry in list(data['page_history']):
            if not isinstance(entry, float):
                history_liste.append(entry[2:-2].split("', '"))


def color_fader(c1, c2, mix=0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    """

    :param c2:
    :param c1:
    :type mix: float
    """
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


def invert_arrowheads(graph):
    for edge in graph.edges():
        edge.attr['arrowhead'] = 'inv'


def create_stack_list(input_list):
    """

    :param input_list: list (of page visits), duplicates are possible
    :return: stack list: loops have been removed, consecutive duplicates also have been removed
    """
    # print('#################')
    # print(input_list)
    stack_list = []
    list_of_backward_jumps = []

    for i in range(0, len(input_list)):
        if i > 0 and input_list[i] == input_list[i-1]:
            continue

        if input_list[i] not in stack_list:
            stack_list.append(input_list[i])
        else:
            list_of_backward_jumps.append((stack_list.pop(), input_list[i]))
    if 'end' in input_list:
        print('sprünge nach "end":')
        print(input_list[input_list.index('end'):])

    # print(stack_list)
    return stack_list, list_of_backward_jumps

