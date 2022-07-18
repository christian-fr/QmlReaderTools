from networkx import DiGraph, node_connected_component
import networkx as nx

edges_data = [('index', 'index', {'label': '([0] var01 != 1 & \n flag_index != 1)'}), ('index', 'cancel1', {'label': '([1] var01 != 1 & \n flag_index == 1)'}), ('index', 'offer', {'label': '([2] jsCheck == 1 & \n isMobile == 1 & \n width == 1 lt 400 & \n var01 == 1)'}), ('index', 'A01', {'label': '([3] var01 == 1)'}), ('cancel1', 'end', {'label': ''}), ('offer', 'A01', {'label': ''}), ('A01', 'A01', {'label': '([0] var02 == MISS & \n flag_A01 != 1)'}), ('A01', 'cancel2', {'label': '([1] var02 == MISS & \n flag_A01 == 1)'}), ('A01', 'A02', {'label': '([2] var02 == 3)'}), ('A01', 'A03', {'label': '([3] var02 == 4)'}), ('A01', 'A05', {'label': '([4] var02 == 1)'}), ('A01', 'A04', {'label': '([5] var02 == 2) |\n([6] var02 != 2])'}), ('A01', 'A06', {'label': '([7] var02 == MISS)'}), ('cancel2', 'end', {'label': ''}), ('A02', 'A04', {'label': ''}), ('A03', 'A05', {'label': ''}), ('A05', 'A06', {'label': ''}), ('A04', 'A05', {'label': ''}), ('A06', 'A07', {'label': ''}), ('A07', 'A08', {'label': ''}), ('A08', 'A09', {'label': ''}), ('A09', 'A10', {'label': ''}), ('A10', 'A11', {'label': ''}), ('A11', 'A12', {'label': ''}), ('A12', 'A13', {'label': ''}), ('A13', 'A14', {'label': ''}), ('A14', 'A15', {'label': ''}), ('A15', 'A16', {'label': ''}), ('A16', 'A17', {'label': ''}), ('A17', 'A18', {'label': ''}), ('A18', 'A19', {'label': ''}), ('A19', 'A20', {'label': ''}), ('A20', 'A21', {'label': ''}), ('A21', 'A22', {'label': ''}), ('A22', 'A23', {'label': ''}), ('A23', 'A24', {'label': ''}), ('A24', 'A25', {'label': ''}), ('A25', 'A26', {'label': ''}), ('A26', 'A27', {'label': ''}), ('A27', 'A29', {'label': ''}), ('A29', 'A30', {'label': ''}), ('A28', 'A29', {'label': ''}), ('A30', 'A31', {'label': ''}), ('A31', 'A32', {'label': ''}), ('A32', 'A33', {'label': ''}), ('A33', 'A34', {'label': ''}), ('A34', 'A35', {'label': ''}), ('A35', 'A36', {'label': ''}), ('A36', 'A37', {'label': ''}), ('A37', 'A38', {'label': ''}), ('A38', 'A39', {'label': ''}), ('A39', 'A50', {'label': ''}), ('A50', 'A51', {'label': ''}), ('A51', 'A52', {'label': ''}), ('A52', 'A53', {'label': ''}), ('A53', 'A54', {'label': ''}), ('A54', 'cancel1', {'label': ''})]
nodes_data = ['index', 'cancel1', 'offer', 'A01', 'cancel2', 'A02', 'A03', 'A05', 'A04', 'A06', 'A07', 'A08', 'A09', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15', 'A16', 'A17', 'A18', 'A19', 'A20', 'A21', 'A22', 'A23', 'A24', 'A25', 'A26', 'A27', 'A29', 'A28', 'A30', 'A31', 'A32', 'A33', 'A34', 'A35', 'A36', 'A37', 'A38', 'A39', 'A50', 'A51', 'A52', 'A53', 'A54', 'end']

di_graph = DiGraph()

[di_graph.add_node(node) for node in nodes_data]
[di_graph.add_edge(edge[0], edge[1]) for edge in edges_data]

for node in di_graph.nodes:
    print(str(node).split('\n')[0])
    print(di_graph.in_degree[node])



# load gml data
# di_graph2 = nx.read_gml(r'/media/a/virtualbox/flowcharts/2021-01-27_15-34-47_2021-01-27_questionnaire_generated_HISBUS_Pretest.gml')
di_graph2 = nx.read_gml('../flowcharts/2021-01-30_01-18-09_questionnaire.gml')

nodes_data = list(di_graph2.nodes)
edges_data = list(di_graph2.edges)

print(('#'*100 + '\n')*2)

# Python program to print all paths from a source to destination.

from collections import defaultdict

# This class represents a directed graph
# using adjacency list representation
# This code is contributed by Neelam Yadav
class Graph:
    """
    This class represents a directed graph
    using adjacency list representation
    This code is contributed by Neelam Yadav
    """
    def __init__(self, vertices, dict_integer_to_pagename, print_path_indices=False):
        # No. of vertices
        self.V = vertices
        self.dict_integer_to_pagename = dict_integer_to_pagename
        self.print_path_indices = print_path_indices
        # default dictionary to store graph
        self.graph = defaultdict(list)

        # function to add an edge to graph

    def add_edge(self, u, v):
        self.graph[u].append(v)

    # A recursive function to print all paths from 'u' to 'd'.
    # visited[] keeps track of vertices in current path.
    # path[] stores actual vertices and path_index is current
    # index in path[]

    def print_all_paths_util(self, u, d, visited, path, path_readable):

        # Mark the current node as visited and store in path
        visited[u] = True
        path.append(u)
        path_readable.append(self.dict_integer_to_pagename[u])

        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            if self.print_path_indices:
                print(path)
            print(path_readable)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if not visited[i]:
                    self.print_all_paths_util(i, d, visited, path, path_readable)

                    # Remove current vertex from path[] and mark it as unvisited
        path_readable.pop()
        path.pop()
        visited[u] = False

    # Prints all paths from 's' to 'd'
    def print_all_paths(self, s, d):

        # Mark all the vertices as not visited
        visited = [False] * self.V

        # Create an array to store paths
        path = []
        path_readable = []

        # Call the recursive helper function to print all paths
        self.print_all_paths_util(s, d, visited, path, path_readable)


pagename_list = list(set(nodes_data))
tmp_dict_pagename_to_integer = {}
tmp_dict_integer_to_pagename = {}
for pagename in pagename_list:
    tmp_dict_pagename_to_integer[pagename] = pagename_list.index(pagename)
    tmp_dict_integer_to_pagename[pagename_list.index(pagename)] = pagename

g = Graph(len(nodes_data), tmp_dict_integer_to_pagename)
[g.add_edge(tmp_dict_pagename_to_integer[entry[0]], tmp_dict_pagename_to_integer[entry[1]]) for entry in edges_data]
print(g.print_all_paths(tmp_dict_pagename_to_integer['index'], tmp_dict_pagename_to_integer['A05']))


list_of_relevant_nodes =  ['index', 'A06', 'A08']
list_of_relevant_nodes_indices = [tmp_dict_pagename_to_integer[entry] for entry in list_of_relevant_nodes]

for i in range(len(list_of_relevant_nodes_indices)-1):
    print(f'listing all paths between [{list_of_relevant_nodes_indices[i]}] and [{list_of_relevant_nodes_indices[i+1]}]:\n')
    print(g.print_all_paths(list_of_relevant_nodes_indices[i], list_of_relevant_nodes_indices[i+1]))

# optimize graph - deflate, pop unnecessary nodes, save variable information

# step 1: generate list of all nodes with out_degree == 1:
deflate_start_possible_nodes_list = [node for node in di_graph.nodes if di_graph.in_degree[node] == 1 ]
deflate_end_possible_nodes_list = [node for node in di_graph.nodes if di_graph.out_degree[node] == 1 ]

deflation_candidates_list = [node for node in deflate_start_possible_nodes_list if node in deflate_end_possible_nodes_list]

for node in deflation_candidates_list:
    target_node_list = [edge[1] for edge in di_graph.edges if edge[0] == node]
    assert len(target_node_list) == 1
    target_node = target_node_list[0]

    # ToDo: copy variable to new cumulative page object

    new_node_label = str(node) + ',' + str(target_node)
    di_graph.add_node(new_node_label)

    list_of_edge_targets_from_target_node = [edge[1] for edge in di_graph.edges if edge[0] == target_node]
    #  ToDo: further work needed!!!!
    # [di_graph.add_edge(new_node_label, ) ]


def look_for_bottleneck_nodes(di_graph_object, list_of_nodes_to_remove):
    assert isinstance(di_graph_object, nx.DiGraph)
    assert isinstance(list_of_nodes_to_remove, list) or list_of_nodes_to_remove is None
    assert nx.is_weakly_connected(di_graph_object)

    if list_of_nodes_to_remove is not None:
        for node in list_of_nodes_to_remove:
            di_graph_object.remove_node(node)
    for node in di_graph_object.nodes:
        tmp_di_graph_object_copy = di_graph_object.copy()
        tmp_di_graph_object_copy.remove_node(node)
        if not nx.is_weakly_connected(tmp_di_graph_object_copy):
            print(node)
            # print(nx.is_strongly_connected(tmp_di_graph_object_copy))
            nx.is_strongly_connected(di_graph_object)
            tmp_list_connected_components = list(nx.connected_components(nx.to_undirected(di_graph_object)))
            print(len(tmp_list_connected_components))
            print(tmp_list_connected_components)


nx.is_weakly_connected(di_graph2)
look_for_bottleneck_nodes(di_graph2, list_of_nodes_to_remove=['cancel1', 'cancel2', 'end'])

print(list(nx.connected_components(nx.to_undirected(di_graph2))))
