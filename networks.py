# loads empirical network & builds synthetic food web graphs and loads them. Erdos Renyi and PNM.

import networkx as nx
import numpy as np

def load_little_rock_lake(filepath="maayan-foodweb/out.maayan-foodweb"):
    # loads the little rock lake food web and returns directed graph prey-> predator
    G = nx.DiGraph()
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("%") or line.startswith("#"):
                continue
            prey, predator = map(int, line.split()[:2])
            G.add_edge(prey, predator)
    return G