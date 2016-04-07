import json
import random

import algorithms
from visualise import Visualiser

with open('config.json', 'r') as f:
    config = json.load(f)

random.seed(config['global']['seed'])
algorithm_class = config['global']['world_algorithm']
world_algorithm = getattr(algorithms, algorithm_class)
world = world_algorithm(config)
history = world.go()
# print (history_list)
if config["visualise"]:
    visualiser = Visualiser()
    entities_to_plot = config['global']['properties_to_plot']
    for entity, properties_to_plot in entities_to_plot.items():
        for prop in properties_to_plot:
            visualiser.plot(history, prop, entity)
