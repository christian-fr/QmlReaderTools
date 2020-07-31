import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import pygraphviz
import matplotlib.pyplot as plt
import

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

liste = []
for entry in list(data['page_history']):
    if not isinstance(entry, float):
        liste.append(entry[2:-2].split("', '"))


dict_of_edges = {}

for entry in liste:
    index = 0
    while index < len(entry)-1:
        if tuple([entry[index], entry[index+1]]) in dict_of_edges.keys():
            dict_of_edges[tuple([entry[index], entry[index + 1]])] += 1
        else:
            dict_of_edges[tuple([entry[index], entry[index+1]])] = 1
        index += 1

graph = nx.Graph()
for key, val in dict_of_edges.items():
    print(key)
    print(val)
    graph.add_edge(key[0], key[1])
    graph.get_edge_data(key[0], key[1])['weight'] = val

print(graph.edges)

pos = graphviz_layout(graph, prog='dot')
nx.draw(graph, pos, with_labels=True)



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