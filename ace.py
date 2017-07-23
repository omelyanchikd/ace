import json
import random

import algorithms
from visualise import Visualiser

with open('model_config.json', 'r') as f:
    model_config = json.load(f)

with open('model_run_config.json', 'r') as f:
    config = json.load(f)

model_config = model_config['fields']
config = config['fields']

random.seed(config['global']['seed'])
algorithm_class = config['global']['world_algorithm']
world_algorithm = getattr(algorithms, algorithm_class)
world = world_algorithm(model_config, config)
history = world.go()
# print (history_list)
graphs = []
if config["visualise"]:
    visualiser = Visualiser()
    entities_to_plot = config['global']['properties_to_plot']
    for entity, properties_to_plot in entities_to_plot.items():
        for prop in properties_to_plot:
            graphs.append(visualiser.plot(history, prop, entity, False))
