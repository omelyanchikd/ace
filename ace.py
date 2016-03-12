from world import World
import json

with open('config.json', 'r') as f:
    config = json.load(f)

world = World(config)
world.go()
