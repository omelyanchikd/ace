import json
import random

import algorithms
from visualise import Visualiser

def run_ace(model_config_json, run_config_json):
    model_config = json.loads(model_config_json)
    run_config = json.loads(run_config_json)

    model_config = model_config[0]['fields']
    run_config = run_config[0]['fields']

#random.seed(config['global']['seed'])
#algorithm_class = config['global']['world_algorithm']
#world_algorithm = getattr(algorithms, algorithm_class)
#world = world_algorithm(model_config, config)

    world = algorithms.BasicWorld(model_config, run_config)
    history = world.go()
    return history