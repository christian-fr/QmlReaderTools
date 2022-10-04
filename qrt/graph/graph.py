import argparse
import os
from pathlib import Path
from typing import List, Optional
from qrt.util.xml import flatten
import networkx as nx
from qrt.util.xml import Questionnaire, read_xml
# import pygraphviz
import numpy as np
import matplotlib as mpl


def color_fader(c1, c2, mix=0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    """
    :param c2:
    :param c1:
    :type mix: float
    """
    c1 = np.array(mpl.colors.to_rgb(c1))
    c2 = np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)


def create_blue_red_color_gradient_list(steps: int = 256) -> List[str]:
    """
    :param steps:
    :return: list of color values
    """
    c1 = 'blue'
    c2 = 'red'
    n = steps
    color_gradient_list = [color_fader(c1, c2, i / n) for i in range(0, n)]
    return color_gradient_list


def color_str_to_hex(color_str: str) -> str:
    return mpl.colors.to_hex(np.array(mpl.colors.to_rgb(color_str)))


def create_digraph(q: Questionnaire, color_edges: Optional[dict],
                   output_file: str,
                   color_nodes: Optional[dict] = None,
                   remove_dead_ends: bool = True,
                   label_edges: bool = False
                   ) -> nx.DiGraph:
    g = nx.DiGraph()

    # l = create_blue_red_color_gradient_list()

    blac_list_cumu = []
    blue_list_cumu = []
    pink_list_cumu = []
    gree_list_cumu = []
    oran_list_cumu = []
    cyan_list_cumu = []
    red_list_cumu = []
    lime_list_cumu = []
    yell_list_cumu = []

    frag_vars_str = ','.join([f'episodes_fragment_{i}' for i in range(1, 101)])

    for page in q.pages:
        # regular transitions
        # black
        blac_list = [transition for transition in page.transitions
                     if transition.target_uid != 'episodeDispatcher' or page.uid == 'calendar']
        blac_list_cumu += blac_list

        if label_edges:
            [g.add_edge(page.uid, transition.target_uid, label=transition.condition.replace(frag_vars_str, '...'),
                        color=color_edges[0]) for transition in blac_list if transition.condition is not None]
            [g.add_edge(page.uid, transition.target_uid, color=color_edges[0]) for transition in blac_list if
             transition.condition is None]
        else:
            [g.add_edge(page.uid, transition.target_uid, color=color_edges[0]) for transition in blac_list]

        # blue
        blue_list = [transition for transition in page.transitions
                     if transition.target_uid == 'episodeDispatcher' and page.uid != 'calendar']
        blue_list_cumu += blue_list
        [g.add_edge(page.uid, transition.target_uid, color=color_edges[1]) for transition in blue_list]

        # trigger redirects
        # red
        red_list = [[target_tuple[0] for target_tuple in trigger.target_cond_list
                     if target_tuple[0] not in ['calendar', 'episodeDispatcher']
                     and target_tuple[1] not in ['episodeDispatcher']]
                    for trigger in page.trig_redirect_on_exit_false]
        red_list_flat = flatten(red_list)
        if red_list_flat:
            red_list_cumu.append((page.uid, red_list_flat))
        [g.add_edge(page.uid, target_uid, color=color_edges[6]) for target_uid in red_list_flat]

        # green
        gree_list = [[target_tuple[0] for target_tuple in trigger.target_cond_list
                      if 'zofar.asNumber(episode_index) lt 0' in target_tuple[1]]
                     for trigger in page.trig_redirect_on_exit_false]
        gree_list_flat = flatten(gree_list)
        if gree_list_flat:
            gree_list_cumu.append((page.uid, gree_list_flat))
            [g.add_edge(page.uid, target_uid, color=color_edges[3]) for
             target_uid in gree_list_flat]

        # orange
        orange_list = [[target_tuple[0] for target_tuple in trigger.target_cond_list
                        if target_tuple[0] == 'episodeDispatcher']
                       for trigger in page.trig_redirect_on_exit_false]
        orange_list_flat = flatten(orange_list)
        if orange_list_flat:
            oran_list_cumu.append((page.uid, orange_list_flat))
            [g.add_edge(page.uid, target_uid, color=color_edges[4]) for target_uid in orange_list_flat]

        # cyan
        cyan_list = [[target_tuple[0] for target_tuple in trigger.target_cond_list if
                      page.uid == 'episodeDispatcher']
                     for trigger in page.trig_redirect_on_exit_false]
        cyan_list_flat = flatten(cyan_list)
        if cyan_list_flat:
            cyan_list_cumu.append((page.uid, cyan_list_flat))
            [g.add_edge(page.uid, target_uid, color=color_edges[5]) for target_uid in cyan_list_flat]

        # pink
        pink_list = [[target_tuple[0] for target_tuple in trigger.target_cond_list if
                      target_tuple[0] == 'calendar']
                     for trigger in page.trig_redirect_on_exit_false]
        pink_list_flat = flatten(pink_list)
        if pink_list_flat:
            pink_list_cumu.append((page.uid, pink_list_flat))
            [g.add_edge(page.uid, target_uid, color=color_edges[2]) for target_uid in pink_list_flat]

        # lime
        lime_list = [[target_tuple[0] for target_tuple in trigger.target_cond_list]
                     for trigger in page.trig_redirect_on_exit_true]
        lime_list_flat = flatten(lime_list)
        if lime_list_flat:
            lime_list_cumu.append((page.uid, lime_list_flat))
            [g.add_edge(page.uid, target_uid, color=color_edges[7]) for target_uid in
             lime_list_flat]

        # page colors
        if color_nodes is not None:
            if page.uid.startswith('defaultLanding'):
                g.add_node(page.uid, {"color": color_nodes[1]})
            if page.uid.startswith('splitLanding'):
                g.add_node(page.uid, {"color": color_nodes[2]})

    print(f'{blac_list_cumu=}')
    print(f'{blue_list_cumu=}')
    print(f'{pink_list_cumu=}')
    print(f'{gree_list_cumu=}')
    print(f'{oran_list_cumu=}')
    print(f'{cyan_list_cumu=}')
    print(f'{red_list_cumu=}')
    print(f'{lime_list_cumu=}')

    if remove_dead_ends:
        while [node for node in g if node not in [edge[0] for edge in g.edges] if node != 'end'] + \
                [node for node in g if node not in [edge[1] for edge in g.edges] if node != 'index'] != []:
            no_out_edges = [node for node in g if node not in [edge[0] for edge in g.edges] if node != 'end']
            no_in_edges = [node for node in g if node not in [edge[1] for edge in g.edges] if node != 'index']

            [g.remove_node(node) for node in no_in_edges + no_out_edges]

    # change color of nodes

    t = nx.nx_agraph.to_agraph(g)

    t.layout('dot')

    t.draw(output_file)
    # t.draw('output/test.svg')

    # t.write('output/test.dot')

    return g


def main(xml_source: str, output_file: str):
    q = read_xml(Path(xml_source))

    _COLOR_STR_DICT = {0: 'black', 1: 'blue', 2: 'pink',
                       3: 'green', 4: 'orange', 5: 'cyan',
                       6: 'red', 7: 'lime', 8: 'yellow'}
    color_edges = {k: color_str_to_hex(v) for k, v in _COLOR_STR_DICT.items()}
    color_grey = {k: color_str_to_hex('grey') for k in _COLOR_STR_DICT.keys()}

    module_prefixes = ['emp', 'voc', 'int', 'job', 'sem', 'fam', 'mpl', 'sco', 'stu', 'oth', 'doc']
    for module_prefix in module_prefixes:
        module_output_file = f'{os.path.splitext(output_file)[0]}_{module_prefix}{os.path.splitext(output_file)[1]}'
        filter_list = ['episodeDispatcher', 'calendar']
        filter_startswith_list = [f'{module_prefix}', f'backwardsBlock_{module_prefix}',
                                  f'defaultLanding_{module_prefix}', f'splitLanding_{module_prefix}']
        filter_startswith_list = [f'{module_prefix}', f'backwardsBlock_{module_prefix}',
                                  f'defaultLanding_{module_prefix}']
        q.filter(filter_list=filter_list, filter_startswith_list=filter_startswith_list)
        # remove_trigger__list = []
        # remove_trigger_startswith_list = ['defaultLanding_', 'splitLanding_']
        # q.remove_trigger(remove_trigger_list=remove_trigger__list,remove_trigger_startswith_list=remove_trigger_startswith_list)
        collapse_list = []
        collapse_startswith_list = ['backwardsBlock_']
        q.collapse_pages(collapse_list=collapse_list, collapse_startswith_list=collapse_startswith_list)
        page_to_remove_transitions = ['episodeDispatcher']
        q.remove_transitions(page_to_remove_transitions)
        g = create_digraph(q=q, color_edges=color_edges,
                           color_nodes=None,
                           remove_dead_ends=True,
                           output_file=module_output_file,
                           label_edges=False)
        # g = create_digraph(q, color_grey, color_edges, False)

if __name__ == '__main__':
    version = '0.0.1'

    parser = argparse.ArgumentParser()
    parser.add_argument("xml_source", help="XML input file")
    parser.add_argument("output_file", help="output file")
    ns = parser.parse_args()

    main(**ns.__dict__)
