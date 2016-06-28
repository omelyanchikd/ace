from flask import Flask, render_template

import json
import plotly
import random

import algorithms
from visualise import Visualiser


app = Flask(__name__)
app.debug = True


def get_graphs():
    with open('config.json', 'r') as f:
        config = json.load(f)
    random.seed(config['global']['seed'])
    algorithm_class = config['global']['world_algorithm']
    world_algorithm = getattr(algorithms, algorithm_class)
    world = world_algorithm(config)
    history = world.go()
    # print (history_list)
    graphs = []
    if config["visualise"]:
        visualiser = Visualiser()
        entities_to_plot = config['global']['properties_to_plot']
        for entity, properties_to_plot in entities_to_plot.items():
            for prop in properties_to_plot:
                graphs.append(visualiser.plot(history, prop, entity, False))
    return graphs


@app.route('/')
def index():

    graphs = get_graphs()

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                           ids=ids,
                           graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
