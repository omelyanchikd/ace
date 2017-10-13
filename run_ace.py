import json
import random

import ace.algorithms

#with open('model_config.json', 'r') as f:
#    model_config = json.load(f)

#with open('run_config.json', 'r') as f:
#    run_config = json.load(f)

def run_ace(model_config_json, run_model_config_json):
    model_config = json.loads(model_config_json)
    run_config = json.loads(run_model_config_json)

    model_config = model_config[0]['fields']
    run_config = run_config[0]['fields']

    world = ace.algorithms.BasicWorld(model_config, run_config)
    history = world.go()
    return history


#random.seed(config['global']['seed'])
#algorithm_class = config['global']['world_algorithm']
#world_algorithm = getattr(algorithms, algorithm_class)
#world = world_algorithm(model_config, config)

# print (history_list)
#graphs = []
#if config["visualise"]:
#    visualiser = Visualiser()
#    entities_to_plot = config['global']['properties_to_plot']
#    for entity, properties_to_plot in entities_to_plot.items():
#        for prop in properties_to_plot:
#            graphs.append(visualiser.plot(history, prop, entity, False))
