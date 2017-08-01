import json
import random

import algorithms
from visualise import Visualiser

with open('model_config.json', 'r') as f:
    model_config = json.load(f)

with open('run_config.json', 'r') as f:
    run_config = json.load(f)

model_config = model_config[0]['fields']
run_config = run_config[0]['fields']

#random.seed(config['global']['seed'])
#algorithm_class = config['global']['world_algorithm']
#world_algorithm = getattr(algorithms, algorithm_class)
#world = world_algorithm(model_config, config)

world = algorithms.BasicWorld(model_config, run_config)
history = world.go()
# print (history_list)
#graphs = []
#if config["visualise"]:
#    visualiser = Visualiser()
#    entities_to_plot = config['global']['properties_to_plot']
#    for entity, properties_to_plot in entities_to_plot.items():
#        for prop in properties_to_plot:
#            graphs.append(visualiser.plot(history, prop, entity, False))
