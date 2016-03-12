import json
import algorithms

with open('config.json', 'r') as f:
    config = json.load(f)

algorithm_class = config['global']['world_algorithm']
world_algorithm = getattr(algorithms, algorithm_class)
world = world_algorithm(config)
world.go()
