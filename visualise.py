import plotly
from plotly.graph_objs import Scatter, Layout


class Visualiser:
    def plot(self, history, prop, entity):
        data = []
        print('Generating plot for ' + entity + ':' + prop)
        filename = ''

        if entity == 'firm':
            for firm_history in history.firms_history:
                line = getattr(firm_history, prop)
                data.append(Scatter(x=list(range(len(line))), y=list(line), name=firm_history.title))
            filename = 'graphs/' + prop + '.html'

        if entity == 'world':
            line = getattr(history.world_history, prop)
            data.append(Scatter(x=list(range(len(line))), y=list(line), name=history.world_history.title))
            filename = 'graphs/world_' + prop + '.html'

        plotly.offline.plot(figure_or_data={
            "data": data,
            "layout": Layout(
                title=entity + " " + prop
            )
        }, filename=filename)
