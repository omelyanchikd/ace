from flask import Flask, render_template, flash
from form import AppForm
import json
import plotly
import random
import algorithms
from visualise import Visualiser

app = Flask(__name__)
app.debug = False
app.secret_key = 'non-production-secret-key'


def get_graphs(config):
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


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AppForm()

    if form.validate_on_submit():
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['global']['steps'] = int(form.steps.data)
        try:
            firms = json.loads(form.firms.data)
        except ValueError as e:
            flash('Please enter correct json!', 'error')
            return render_template('form.html',
                           title='Run app',
                           form=form)

        print(firms)
        config['algorithms'] = firms
        graphs = get_graphs(config)
        ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
        titles = [graph['layout']['title'] for _, graph in enumerate(graphs)]
        graph_json = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('index.html',
                               ids=ids,
                               graphJSON=graph_json,
                               titles=titles)

    return render_template('form.html',
                           title='Run app',
                           form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
