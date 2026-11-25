###
# File for all removal methods and testing robustness
# Random, out degree (most relied upon nodes/most predators), food-web page rank, trophic level.

import networkx as nx #scipy pulled in by nx automatically
import numpy as np

def get_basal_species(G):
    return {
        node for node in G.nodes()
        if len([p for p in G.predecessors(node) if p != node]) == 0 #no self-loops, no prey for base species
    }

def trigger_secondary_extinctions(G, basal_nodes):
    # this function removes species that have no prey left as an effect of removing a primary species removal
    # removing all species that's gonna die off once a species is removed.
    secondary_lost = 0
    while True:
        starved = [
            node for node in G.nodes()
            if node not in basal_nodes
            and len([p for p in G.predecessors(node) if p != node]) == 0
        ]
        if not starved:
            break
        G.remove_nodes_from(starved)
        secondary_lost += len(starved)
    return secondary_lost

def compute_trophic_levels(G, basal_nodes):
    # metadata for species trophic level, what's its distance from basal species.
    tl = {b: 1.0 for b in basal_nodes if b in G} # assigns trophic level 1.0 for autotrophs
    # the for loop below calculates the mean distance of a species from all basal species
    for node in G.nodes():
        if node in tl:
            continue
        paths = [
            nx.shortest_path_length(G, b, node)
            for b in basal_nodes if b in G and nx.has_path(G, b, node)
        ]
        tl[node] = 1.0 + (np.mean(paths) if paths else 0.0)
    return tl

def pick_target(G, method, basal_nodes):
    # picks the next species to remove based on method (out-degree, page rank, trophic level)
    if method == "random":
        return np.random.choice(list(G.nodes()))
    if method == "out_degree":
        scores = dict(G.out_degree())
    elif method == "pagerank":
        scores = nx.pagerank(G, alpha=0.85)
    elif method == "trophic_top_down":
        scores = compute_trophic_levels(G, basal_nodes)
    elif method == "trophic_bottom_up":
        tl = compute_trophic_levels(G, basal_nodes)
        return min(tl, key=tl.get)
    return max(scores, key=scores.get)

def run_removal(G_orig, method="out_degree"):
    # simulates sequential species removal and tracks primary vs. secondary extinctions until the web collapses
    G = G_orig.copy()
    S = G.number_of_nodes()
    basal_nodes = get_basal_species(G)

    primary = 0
    secondary = 0
    x_vals, y_vals = [0.0], [0.0]
    r50 = None

    while G.number_of_nodes() > 0:
        target = pick_target(G, method, basal_nodes)
        G.remove_node(target)
        primary += 1
        secondary += trigger_secondary_extinctions(G, basal_nodes)

        if r50 is None and (primary + secondary) / S >= 0.50:
            r50 = primary / S

        x_vals.append(primary / S)
        y_vals.append(secondary / S)

    return x_vals, y_vals, r50