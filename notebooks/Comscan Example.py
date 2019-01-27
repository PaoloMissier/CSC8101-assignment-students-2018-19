"""Entry point for sequential community scanner"""

import os
import config as cfg
from comscan.inout import parser
from comscan.algorithms.girvan_newman import girvan_newman_generator
from comscan.algorithms.girvan_newman import girvan_newman
from comscan.view.visualiser import draw
from time import time

# maximum numbers of edges to be parsed.
EDGES_LIMIT = 1000

# Level of communities in Girvan-Newman algorithm
# Defines number of communities desired
COMPONENTS_LEVEL = 5

# If True, the graph will be visualised. Keep false for graphs with more than 100 edges
DRAW = False

DISPLAY_ALL_COMPONENTS = False

if __name__ == '__main__':

    edges_path = "./data/edge_sample.csv"
    source_header, target_header, weight_header = parser.get_headers(edges_path)

    # Parse with edges limit:
    graph = parser.parse(edges_path, edge_limit=EDGES_LIMIT,
                  source_header=source_header, target_header=target_header, weight_header=weight_header)

    number_of_edges = len(list(graph.edges))

    before_time = time()

    components = girvan_newman(graph, COMPONENTS_LEVEL)

    elapsed_time = time() - before_time

    print('Edges: {0};\t\tTarget Level: {1};\t\t\tSequential Computing Time (seconds): {2}\n\n'.format(
        number_of_edges, COMPONENTS_LEVEL, elapsed_time
    ))

    print(components)

    if DRAW:
        draw(graph)

    if DISPLAY_ALL_COMPONENTS:
        for components in girvan_newman_generator(graph):
            print(len(components), components)
