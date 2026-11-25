# file will be used for producing figure to display results. mainly based on robustness score (R_50)

import json # lets file read saved results from a json file
from pathlib import Path # confirms that results folder exists before saving to it
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from cascades import get_basal_species, compute_trophic_levels, run_removal

def draw_foodweb(G, z):
    """Draws G arranged vertically by trophic level so food-web layers are visible."""
    colors = ['#d61111', '#11c6d6', '#d67711', '#11d646', '#1b11d6', '#d611cc']
    node_colors = [colors[int(z[i])] for i in G.nodes()]

    # Compute trophic level for vertical (y) placement and spread nodes horizontally (x)
    basal = get_basal_species(G)
    tl = compute_trophic_levels(G, basal)
    pos = {}
    for idx, node in enumerate(sorted(G.nodes(), key=lambda n: tl[n])):
        # Small jitter on x so nodes at the same trophic level don't stack on top of each other
        pos[node] = (idx % 25 + np.random.uniform(-0.3, 0.3), tl[node])

    plt.figure(figsize=(8, 5))
    nx.draw_networkx_edges(G, pos, alpha=0.12, width=0.6, arrows=False)
    nx.draw_networkx_nodes(G, pos, node_size=60, node_color=node_colors)
    plt.ylabel("Trophic Level")
    plt.xticks([])
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)
    plt.gca().spines["bottom"].set_visible(False)
    plt.tight_layout()
    plt.show()

def build_trophic_partition(G):
    # builds a partition of the nodes in G based on their trophic level (basal, intermediate, top predator)
    basal = get_basal_species(G)
    z = {}
    for node in G.nodes():
        if node in basal:
            z[node] = 0  # red (plants / basal species)
        elif G.out_degree(node) == 0:
            z[node] = 2  # orange (top predators)
        else:
            z[node] = 1  # cyan (intermediate consumers)
    return z


def plot_extinction_curves(G, n_random=100):
    # runs each removal strategy and plots secondary extinctions against a random baseline
    strategies = [
        ("Most Eaten First (Out-Degree)", "out_degree", "#d61111"),
        ("PageRank", "pagerank", "#11c6d6"),
        ("Top-Down (Apex Predators First)", "trophic_top_down", "#d67711"),
        ("Bottom-Up (Basal Species First)", "trophic_bottom_up", "#11d646"),
    ]

    plt.figure(figsize=(7, 5))

    # plot each targeted strategy
    for name, method, color in strategies:
        x, y, r50 = run_removal(G, method=method)
        plt.plot(x, y, color=color, linewidth=2, label=f"{name} (R50 = {r50:.2f})")

    # run random removal multiple times and average the curves
    x_grid = np.linspace(0, 1, 101)
    all_rand_y = []
    all_rand_r50 = []

    for i in range(n_random):
        xr, yr, r50_r = run_removal(G, method="random")
        all_rand_y.append(np.interp(x_grid, xr, yr))
        all_rand_r50.append(r50_r)

    avg_rand_y = np.mean(all_rand_y, axis=0)
    avg_rand_r50 = np.mean(all_rand_r50)
    plt.plot(x_grid, avg_rand_y, "k--", linewidth=2, label=f"Random Baseline (R50 = {avg_rand_r50:.2f})")

    # reference line showing the maximum possible secondary extinctions
    plt.plot([0, 1], [1, 0], color="gray", linestyle=":", linewidth=1)

    plt.xlabel("Fraction of Species Removed")
    plt.ylabel("Fraction of Secondary Extinctions")
    plt.title("Food Web Robustness Under Different Removal Strategies")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend(frameon=False, fontsize=8.5)
    plt.tight_layout()
    plt.show()