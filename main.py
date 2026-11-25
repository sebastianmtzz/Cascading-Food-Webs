# driver for all files
import json
from pathlib import Path
import numpy as np

import networks
import cascades
import plots

G = networks.load_little_rock_lake()

# draw the food web colored by trophic role
z = plots.build_trophic_partition(G)
plots.draw_foodweb(G,z)

# plot the secondary extinction curves and R50 scores
plots.plot_extinction_curves(G, n_random=100)