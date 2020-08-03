# POSTGRESQL QUERY to get a csv of all relevant transitionss
# SELECT DISTINCT (p.token) as token, (SELECT '["' || string_agg(s.page, '" , "' ORDER BY s.timestamp asc)||'"]' FROM surveyhistory s WHERE participant_id=p.id) as history FROM participant p, surveyhistory s WHERE p.id=s.participant_id;



#import sys
import os
import pandas as pd
import networkx as nx
import math
# from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import pygraphviz
# import matplotlib.pyplot as plt
from math import ceil

data_input_file = r'wide_dataset_with_page_history_as_list.csv'


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
    stack_list = []

    for i in range(0, len(input_list)):
        if i > 0 and input_list[i] == input_list[-i]:
            continue

        if input_list[i] not in stack_list:
            stack_list.append(input_list[i])
        else:
            stack_list.pop()

    return stack_list


x = [(len(i), len(set(i)), len(create_stack_list(i))) for i in history_liste]

index = 0
for length, length_set, length_stack in x:
    if length_set != length_stack:
        print(str(index), str(length_set), str(length_stack), str(length_stack -length_set))
    index += 1

# Create a list and dict of returning points, i.e. pages that have once been visited, but then the respondent has
#  gone back, changed an answer and took a different path

list_of_returning_points = [set(i) ^ set(create_stack_list(i)) for i in history_liste]

dict_weights_of_returning_points = {}

for liste in history_liste:
    for key in liste:
        if key in dict_weights_of_returning_points:
            if liste.index(key) != len(liste)-1:
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

list_of_effective_paths = [create_stack_list(i) for i in history_liste]

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


outputfile_graph = r'output_graph.png'

input_graph_file = os.path.join(os.getcwd(), '2020-08-03_11-39_questionnaire_corona-sid_final.dot')

flowchart_graph = pygraphviz.agraph.AGraph()

flowchart_graph.read(input_graph_file)

flowchart_graph.layout('dot')


def create_trail(graph, dict_of_weights_of_edges):
    """

    :param graph: input graph, DiGraph form networkx
    :param dict_of_weights_of_edges: dictionary of weights
    :return: tuple of two lists: list of used edges from graph, list of unused edges from graph
    """
    assert isinstance(flowchart_graph, pygraphviz.agraph.AGraph)
    assert isinstance(dict_of_weights_of_effective_edges, dict)
    list_of_used_edges_tuples = []
    list_of_unused_edges_tuples = []
    for edge in flowchart_graph.edges():
        if edge in dict_of_weights_of_effective_edges_normalized.keys():
            list_of_used_edges_tuples.append(tuple(edge))
            print('weigth from dict: ' + str(dict_of_weights_of_effective_edges_normalized[edge]))
            edge.attr['penwidth'] = ceil(dict_of_weights_of_effective_edges_normalized[edge] * 10)
            print('penwidth at edge: ' + str(edge.attr['penwidth']))

        else:
            list_of_unused_edges_tuples.append(tuple(edge))
    print('edges in graph without corresponding edges in data: \n' + str(list_of_unused_edges_tuples))
    return list_of_used_edges_tuples, list_of_unused_edges_tuples


create_trail(flowchart_graph, dict_of_weights_of_effective_edges_normalized)


def create_highlight_points_of_return(graph, dict_of_weights_of_nodes):
    """

    :param graph: input graph, DiGraph form networkx
    :param dict_of_weights_of_nodes: dictionary of weights
    :return: tuple of two lists: list of used nodes from graph, list of unused nodes from graph
    """
    assert isinstance(flowchart_graph, pygraphviz.agraph.AGraph)
    assert isinstance(dict_of_weights_of_nodes, dict)
    list_of_used_nodes_tuples = []
    list_of_unused_nodes_tuples = []
    for node in flowchart_graph.nodes():
        if node in dict_of_weights_of_nodes.keys():
            list_of_used_nodes_tuples.append(tuple(node))
            print('weight from dict: ' + str(dict_of_weights_of_nodes[node]))
            node.attr['penwidth'] = ceil(dict_of_weights_of_nodes[node] * 10)
            print('penwidth at node: ' + str(node.attr['penwidth']))

        else:
            list_of_unused_nodes_tuples.append(tuple(node))
    print('edges in graph without corresponding edges in data: \n' + str(list_of_unused_nodes_tuples))
    return list_of_used_nodes_tuples, list_of_unused_nodes_tuples


create_highlight_points_of_return(flowchart_graph, dict_weights_of_returning_points_normalized)

# flowchart_graph.edges()[0].attr['width'] = 100
# flowchart_graph.edges()[0].attr['penwidth'] = 4
# flowchart_graph.edges()[0].attr['color'] = 'red'
# flowchart_graph.edges()[0].attr['weight'] = 100

flowchart_graph.draw(outputfile_graph)




from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

# Red Color
color1_rgb = sRGBColor(1.0, 0.0, 0.0);

# Blue Color
color2_rgb = sRGBColor(0.0, 0.0, 1.0);

# Convert from RGB to Lab Color Space
color1_lab = convert_color(color1_rgb, LabColor);

# Convert from RGB to Lab Color Space
color2_lab = convert_color(color2_rgb, LabColor);

# Find the color difference
delta_e = delta_e_cie2000(color1_lab, color2_lab);

print("The difference between the 2 color = ", delta_e)