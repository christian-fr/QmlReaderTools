import os
from pathlib import Path
from typing import List
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


def create_digraph(q: Questionnaire) -> nx.DiGraph:
    # color scheme
    COL_TRANS = color_str_to_hex('black')
    COL_RED_ON_EXIT_FALSE = color_str_to_hex('red')
    COL_RED_ON_EXIT_TRUE = color_str_to_hex('blue')
    g = nx.DiGraph()

    l = create_blue_red_color_gradient_list()

    for page in q.pages:
        # regular transitions
        [g.add_edge(page.uid, transition.target_uid, color=color_str_to_hex('black')) for transition in
         page.transitions if transition.target_uid != 'episodeDispatcher' or page.uid == 'calendar']
        [g.add_edge(page.uid, transition.target_uid, color=color_str_to_hex('blue')) for transition in
         page.transitions if transition.target_uid == 'episodeDispatcher' and page.uid != 'calendar']
        # trigger redirects
        [g.add_edge(page.uid, target_uid, color=color_str_to_hex('pink')) for target_uid in flatten([[target_tuple[0]
                                                                                                      for target_tuple
                                                                                                      in
                                                                                                      trigger.target_cond_list
                                                                                                      if target_tuple[
                                                                                                          0] not in ['calendar', 'episodeDispatcher'] and
                                                                                                      target_tuple[1] not in ['episodeDispatcher']]
                                                                                                     for trigger in
                                                                                                     page.trig_redirect_on_exit_false])]

        [g.add_edge(page.uid, target_uid, color=color_str_to_hex('green')) for target_uid in flatten([[target_tuple[0]
                                                                                                       for target_tuple
                                                                                                       in
                                                                                                       trigger.target_cond_list
                                                                                                       if target_tuple[
                                                                                                           0] == 'calendar' and
                                                                                                       target_tuple[
                                                                                                           1] == 'zofar.asNumber(episode_index) lt 0']
                                                                                                      for trigger in
                                                                                                      page.trig_redirect_on_exit_false])]

        [g.add_edge(page.uid, target_uid, color=color_str_to_hex('orange')) for target_uid in flatten([[target_tuple[0]
                                                                                                       for target_tuple
                                                                                                       in
                                                                                                       trigger.target_cond_list
                                                                                                       if target_tuple[
                                                                                                           0] == 'episodeDispatcher']
                                                                                                      for trigger in
                                                                                                      page.trig_redirect_on_exit_false])]

        [g.add_edge(page.uid, target_uid, color=color_str_to_hex('cyan')) for target_uid in flatten([[target_tuple[0]
                                                                                                       for target_tuple
                                                                                                       in
                                                                                                       trigger.target_cond_list
                                                                                                       if target_tuple[
                                                                                                           1] == 'episodeDispatcher']
                                                                                                      for trigger in
                                                                                                      page.trig_redirect_on_exit_false])]

        [g.add_edge(page.uid, target_uid, color=color_str_to_hex('violet')) for target_uid in flatten([[target_tuple[0]
                                                                                                        for target_tuple
                                                                                                        in
                                                                                                        trigger.target_cond_list
                                                                                                        if target_tuple[
                                                                                                            0] == 'calendar' and
                                                                                                        target_tuple[
                                                                                                            1] != 'zofar.asNumber(episode_index) lt 0']
                                                                                                       for trigger in
                                                                                                       page.trig_redirect_on_exit_false])]
        [g.add_edge(page.uid, target_uid, color=color_str_to_hex('blue')) for target_uid in
         flatten([[target_tuple[0] for target_tuple in trigger.target_cond_list] for trigger in
                  page.trig_redirect_on_exit_true])]

        # remove all nodes that have an out_degree of 0 (except end)
        # remove all nodes that have an in_degree of 0 (except index)

    while [node for node in g if node not in [edge[0] for edge in g.edges] if node != 'end'] + \
        [node for node in g if node not in [edge[1] for edge in g.edges] if node != 'index'] != []:

        no_out_edges = [node for node in g if node not in [edge[0] for edge in g.edges] if node != 'end']
        no_in_edges = [node for node in g if node not in [edge[1] for edge in g.edges] if node != 'index']

        [g.remove_node(node) for node in no_in_edges + no_out_edges]

    t = nx.nx_agraph.to_agraph(g)
    t.layout('dot')
    t.draw('test.png')
    return g


def main():
    input_xml = Path(os.path.abspath('.'), 'tests', 'context', 'qml', 'questionnaire_lhc.xml')
    q = read_xml(input_xml)
    g = create_digraph(q)


if __name__ == '__main__':
    main()
