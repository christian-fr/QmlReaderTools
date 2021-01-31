import networkx as nx
import pygraphviz
import pathlib
from collections import defaultdict
import qmlReader.new_questionnaire_classes

di_graph2 = nx.read_gml('/flowcharts/2021-01-30_10-40-51_questionnaire_nacaps.gml')

nodes_data = list(di_graph2.nodes)
edges_data = list(di_graph2.edges)

print(nx.is_weakly_connected(di_graph2))


def draw_graph(di_graph_object, path):
    assert isinstance(di_graph_object, nx.DiGraph)
    assert isinstance(path, str) or isinstance(path, pathlib.Path)
    pgv_a_graph = nx.nx_agraph.to_agraph(di_graph_object)
    pgv_a_graph.draw(path, prog='dot')


# draw_graph(di_graph2, 'test.png')

def remove_list_of_nodes(di_graph_object, list_of_nodes):
    assert isinstance(di_graph_object, nx.DiGraph)
    assert isinstance(list_of_nodes, list) or list_of_nodes is None

    di_graph_object_copy = di_graph_object.copy()

    if list_of_nodes is None:
        return di_graph_object_copy
    for entry in list_of_nodes:
        assert isinstance(entry, str)
        assert entry in di_graph_object_copy.nodes
    # manual removal of nodes
    for node in list_of_nodes:
        di_graph_object_copy.remove_node(node)
    return di_graph_object_copy


print(nx.is_weakly_connected(di_graph2))
print(nx.is_strongly_connected(di_graph2))


def look_for_bottleneck_nodes(di_graph_object, list_of_nodes_to_exclude=None):
    assert isinstance(di_graph_object, nx.DiGraph)
    assert isinstance(list_of_nodes_to_exclude, list) or list_of_nodes_to_exclude is None

    di_graph_object_copy = di_graph_object.copy()
    assert nx.is_weakly_connected(di_graph_object)

    tmp_list_of_bottleneck_nodes = []
    if list_of_nodes_to_exclude is not None:
        di_graph_object_copy = remove_list_of_nodes(di_graph_object_copy, list_of_nodes_to_exclude)
    assert nx.is_weakly_connected(di_graph_object_copy)
    for node in di_graph_object_copy.nodes:
        tmp_di_graph_object_copy = di_graph_object_copy.copy()
        tmp_di_graph_object_copy.remove_node(node)
        if not nx.is_weakly_connected(tmp_di_graph_object_copy):
            tmp_list_of_bottleneck_nodes.append(node)
            # print(node)
            # print(nx.is_strongly_connected(tmp_di_graph_object_copy))
            # nx.is_strongly_connected(di_graph_object)
            # tmp_list_connected_components = list(nx.connected_components(nx.to_undirected(di_graph_object)))
            # print(len(tmp_list_connected_components))
            # print(tmp_list_connected_components)
    return tmp_list_of_bottleneck_nodes


# list_of_bottleneck_nodes = look_for_bottleneck_nodes(di_graph2, list_of_nodes_to_exclude=['cancel1', 'cancel2'])
# print(list_of_bottleneck_nodes)

def find_all_nodes_inbetween(di_graph_object, source, target):
    assert isinstance(di_graph_object, nx.DiGraph)
    di_graph_object_copy = di_graph_object.copy()

    assert isinstance(source, str)
    assert isinstance(target, str)
    assert source in di_graph_object_copy.nodes
    assert target in di_graph_object_copy.nodes
    tmp_list_of_nodes = []
    counter = 0
    for path in nx.all_simple_paths(G=di_graph_object_copy, source=source,
                                    target=target):
        for node in path:
            if node not in tmp_list_of_nodes:
                tmp_list_of_nodes.append(node)
        counter += 1
        if counter % 10000 == 0:
            print(f'[{source}]-[{target}], path nr. {counter}')
    return tmp_list_of_nodes


def find_all_subgraphs(di_graph_object, list_of_nodes_to_exclude=None):
    assert isinstance(di_graph_object, nx.DiGraph)
    di_graph_object_copy = di_graph_object.copy()
    tmp_di_graph_object = remove_list_of_nodes(di_graph_object_copy, list_of_nodes_to_exclude)
    tmp_list_of_bottleneck_nodes = look_for_bottleneck_nodes(tmp_di_graph_object)

    tmp_list_of_subgraph_node_pairs = []

    tmp_subgraph_dict = {}
    tmp_subgraph_dict['graph'] = nx.DiGraph()
    tmp_subgraph_dict['condition'] = qmlReader.new_questionnaire_classes.ConditionObject(condition_string=True)
    subgraph_dict = defaultdict(tmp_subgraph_dict)

    for i in range(len(tmp_list_of_bottleneck_nodes) - 1):
        tmp_list_of_subgraph_node_pairs.append((tmp_list_of_bottleneck_nodes[i], tmp_list_of_bottleneck_nodes[i + 1]))
        subgraph_dict.append()
    tmp_subgraph_nodes_dict = {}
    for node in tmp_list_of_bottleneck_nodes:
        di_graph_object_copy = remove_all_edges_connecting_to_node(di_graph_object_copy, node=node)
    for node_pair in tmp_list_of_subgraph_node_pairs:
        tmp_di_graph_object_copy = di_graph_object_copy.copy()
        # tmp_subgraph_nodes_dict[node_pair] = find_all_nodes_inbetween(di_graph_object=tmp_di_graph_object, source=node_pair[0], target=node_pair[1])
        tmp_subgraph_nodes_dict[node_pair] = nx.node_connected_component(nx.to_undirected(tmp_di_graph_object_copy),
                                                                         node_pair[0])
    return tmp_subgraph_nodes_dict


def remove_all_edges_connecting_to_node(di_graph_object, node):
    assert isinstance(di_graph_object, nx.DiGraph)
    assert isinstance(node, str)
    assert node in di_graph_object.nodes

    di_graph_object_copy = di_graph_object.copy()
    tmp_edges_to_remove_list = []
    for edge in di_graph_object_copy.edges:
        if edge[1] == node:
            tmp_edges_to_remove_list.append(edge)
    [di_graph_object_copy.remove_edge(u=edge[0], v=edge[1]) for edge in tmp_edges_to_remove_list]
    return di_graph_object_copy


# di_graph2_edges_removed = remove_all_edges_connecting_to_node(di_graph2, 'A06')
x = find_all_subgraphs(di_graph2, list_of_nodes_to_exclude=['cancel1', 'cancel2'])
print(x)
