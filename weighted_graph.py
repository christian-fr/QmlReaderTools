__author__ = "Christian Friedrich"
__maintainer__ = "Christian Friedrich"
__license__ = "GPL v3"
__version__ = "0.0.1"
__status__ = "Prototype"
__name__ = "WeightedGraph"


# POSTGRESQL QUERY to get a csv of all relevant transitionss
# SELECT DISTINCT (p.token) as token, (SELECT '["' || string_agg(s.page, '" , "' ORDER BY s.timestamp asc)||'"]' FROM surveyhistory s WHERE participant_id=p.id) as history FROM participant p, surveyhistory s WHERE p.id=s.participant_id;

import os
import pandas as pd
import pygraphviz
from math import ceil

data_input_file = r'data/wide_dataset_with_page_history_as_list.csv'


# ToDo: rewrite this docstring-like stuff - data structure etc.
"""
Data structure necessary for the csv input file::

    '''
    "source", "target", "weight", "color1", "color2", "penwidth"
    "index", "offer", "0.5", "blue", "red", "10"
    "index", "A01", "1.5", "blue", "red", "10" 
    "A01", "A02", "10000", "blue", "red", "10"
    [...]
    '''
after that:
- translate color1 & color2 into rgb values
- calculate color difference between them/ calculate steps between them (using a parameter, more or less fixed) / fixed range of color steps
- assign those color step values according to the corresponding weights
- use those values to highlight / color the corresponding edges in the graph
- error handling: what about connections that are not within the graph? (like opposing direction) --> omit those, send an error message to the logger and to the tkinter messagebox: edges not found
- redraw the graph

medium-term:
- implement this file as a module within this project
- figure out how to do the UI for additionally loading a csv file and redrawing the grpah/flowchart 
- 
"""




data = pd.read_csv(data_input_file, dtype='unicode')

history_liste = []
for entry in list(data['page_history']):
    if not isinstance(entry, float):
        history_liste.append(entry[2:-2].split("', '"))


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


    # print(stack_list)
    return stack_list, list_of_backward_jumps


# x = [(len(i), len(set(i)), len(create_stack_list(i))) for i in history_liste]

# index = 0
# for length, length_set, length_stack in x:
#     if length_set != length_stack:
#         print(str(index), str(length_set), str(length_stack), str(length_stack - length_set))
#     index += 1

# Create a list and dict of returning points, i.e. pages that have once been visited, but then the respondent has
#  gone back, changed an answer and took a different path

list_of_returning_points = [set(i) - set(create_stack_list(i)[0]) for i in history_liste]

list_of_returning_points_clean = [i for i in filter(None, list_of_returning_points)]

dict_weights_of_returning_points = {}

for liste in list_of_returning_points_clean:
    for key in list(liste):
        if key in dict_weights_of_returning_points:
            if list(liste).index(key) != len(liste)-1:
                dict_weights_of_returning_points[key] += 1
        else:
            dict_weights_of_returning_points[key] = 1


tuple_range_of_weights_of_returning_points = tuple([min(dict_weights_of_returning_points.values()), max(dict_weights_of_returning_points.values())])

# normalize values.

dict_weights_of_returning_points_normalized = {}
for key in dict_weights_of_returning_points.keys():
    dict_weights_of_returning_points_normalized[key] = (dict_weights_of_returning_points[key] - tuple_range_of_weights_of_returning_points[0])/(tuple_range_of_weights_of_returning_points[1]-tuple_range_of_weights_of_returning_points[0])


# Create a list and dict of effective paths / edges, i.e. paths that have, in the end (and possibly after subsequent changes)
# been taken through the questionnaire.

list_of_effective_paths = [create_stack_list(i)[0] for i in history_liste]

# ToDo: als function definieren; input: list_of_lists von history-daten (bspw. stacks, backwards, etc.)
dict_of_weights_of_effective_edges = {}

for entry in list_of_effective_paths:
    index = 0
    while index < len(entry)-1:
        if tuple([entry[index], entry[index+1]]) in dict_of_weights_of_effective_edges.keys():
            dict_of_weights_of_effective_edges[tuple([entry[index], entry[index + 1]])] += 1
        else:
            dict_of_weights_of_effective_edges[tuple([entry[index], entry[index + 1]])] = 1
        index += 1

tuple_range_of_weights_of_effective_edges = tuple([min(dict_of_weights_of_effective_edges.values()), max(dict_of_weights_of_effective_edges.values())])

# normalize values.

dict_of_weights_of_effective_edges_normalized = {}
for key in dict_of_weights_of_effective_edges.keys():
    dict_of_weights_of_effective_edges_normalized[key] = (dict_of_weights_of_effective_edges[key] - tuple_range_of_weights_of_effective_edges[0])/(tuple_range_of_weights_of_effective_edges[1]-tuple_range_of_weights_of_effective_edges[0])



list_of_backwards_jumps = [create_stack_list(i)[1] for i in history_liste]

dict_of_weights_of_backwards_jumping_edges = {}

for liste in list_of_backwards_jumps:
    for entry in liste:
        if entry in dict_of_weights_of_backwards_jumping_edges.keys():
            dict_of_weights_of_backwards_jumping_edges[entry] += 1
        else:
            dict_of_weights_of_backwards_jumping_edges[entry] = 1

tuple_range_of_weights_of_backwards_jumping_edges = tuple([min(dict_of_weights_of_backwards_jumping_edges.values()), max(dict_of_weights_of_backwards_jumping_edges.values())])

# normalize values.

dict_of_weights_of_backwards_jumping_edges_normalized = {}
for key in dict_of_weights_of_backwards_jumping_edges.keys():
    dict_of_weights_of_backwards_jumping_edges_normalized[key] = (dict_of_weights_of_backwards_jumping_edges[key] - tuple_range_of_weights_of_backwards_jumping_edges[0])/(tuple_range_of_weights_of_backwards_jumping_edges[1]-tuple_range_of_weights_of_backwards_jumping_edges[0])



outputfile_graph_effective_trail = r'output_graph_trail.png'
outputfile_graph_backwards_jumps = r'output_graph_backwards.png'
outputfile_graph_points_of_return = r'output_graph_points_of_return.png'

input_graph_file = os.path.join(os.getcwd(), 'data/2020-08-03_11-39_questionnaire_corona-sid_final.dot')

flowchart_graph = pygraphviz.agraph.AGraph()

flowchart_graph.read(input_graph_file)

flowchart_graph.layout('dot')

flowchart_graph_effective_trail = flowchart_graph.copy()
flowchart_graph_effective_trail.layout('dot')
flowchart_graph_backwards_jumps = flowchart_graph.copy()
flowchart_graph_backwards_jumps.layout('dot')
flowchart_graph_points_of_return = flowchart_graph.copy()
flowchart_graph_points_of_return.layout('dot')



import matplotlib as mpl
import numpy as np


def colorFader(c1,c2,mix=0): #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

c1='blue'
c2='red'
n=256

colorfader = [colorFader(c1, c2, i/n) for i in range(0, n)]


def create_trail(graph, dict_of_weights_of_edges, colorfader_list, max_line_width=10):
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
    for edge in graph.edges():
        if edge in dict_of_weights_of_edges.keys():
            list_of_used_edges_tuples.append(tuple(edge))
            print('weigth from dict: ' + str(dict_of_weights_of_edges[edge]))
            edge.attr['penwidth'] = ceil(dict_of_weights_of_edges[edge] * max_line_width + 1)
            edge.attr['color'] = colorfader_list[ceil(dict_of_weights_of_edges[edge] * (len(colorfader_list)-1))]
            print('penwidth at edge: ' + str(edge.attr['penwidth']))

        else:
            list_of_unused_edges_tuples.append(tuple(edge))
    print('edges in graph without corresponding edges in data: \n' + str(list_of_unused_edges_tuples))
    return list_of_used_edges_tuples, list_of_unused_edges_tuples


create_trail(flowchart_graph_backwards_jumps, dict_of_weights_of_backwards_jumping_edges_normalized, colorfader)

create_trail(flowchart_graph_effective_trail, dict_of_weights_of_effective_edges_normalized, colorfader)


def create_highlight_points_of_return(graph, dict_of_weights_of_nodes):
    """

    :param graph: input graph, DiGraph form networkx
    :param dict_of_weights_of_nodes: dictionary of weights
    :return: tuple of two lists: list of used nodes from graph, list of unused nodes from graph
    """
    assert isinstance(graph, pygraphviz.agraph.AGraph)
    assert isinstance(dict_of_weights_of_nodes, dict)
    list_of_used_nodes_tuples = []
    list_of_unused_nodes_tuples = []
    for node in graph.nodes():
        if node in dict_of_weights_of_nodes.keys():
            print(node.name)
            list_of_used_nodes_tuples.append(tuple(node))
            print('weight from dict: ' + str(dict_of_weights_of_nodes[node]))
            node.attr['penwidth'] = ceil(dict_of_weights_of_nodes[node] * 10 + 1)
            print('color: ' + str(colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]))
            node.attr['color'] = colorfader[ceil(dict_of_weights_of_nodes[node] * 255)]
            print('penwidth at node: ' + str(node.attr['penwidth']))

        else:
            list_of_unused_nodes_tuples.append(tuple(node))
    print('edges in graph without corresponding edges in data: \n' + str(list_of_unused_nodes_tuples))
    return list_of_used_nodes_tuples, list_of_unused_nodes_tuples


create_highlight_points_of_return(flowchart_graph_points_of_return, dict_weights_of_returning_points_normalized)

def invert_arrowheads(graph):
    for edge in graph.edges():
        edge.attr['arrowhead'] = 'inv'


invert_arrowheads(flowchart_graph_backwards_jumps)

flowchart_graph_effective_trail.draw(outputfile_graph_effective_trail)
flowchart_graph_backwards_jumps.draw(outputfile_graph_backwards_jumps)
flowchart_graph_points_of_return.draw(outputfile_graph_points_of_return)

#
# def two_list_items_next_to_each_other(item1, item2, liste):
#     last_index = 0
#     tmp_list_of_indices = []
#     for i in range(0, liste.count(item1)):
#         last_index += liste[last_index:].index(item1) -1
#         tmp_list_of_indices.append(last_index)
#         last_index += 1
#     print(tmp_list_of_indices)
#     for i in tmp_list_of_indices:
#         x = liste[i+1] == item2
#         a = i
#         z = liste[i]
#         y = liste[i+1]
#         if liste[i+1] == item2:
#             return True
#         else:
#             continue
#     return False
