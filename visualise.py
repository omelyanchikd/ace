import plotly
from plotly.graph_objs import Scatter, Layout


class Visualiser:
    def plot(self, history, prop):
        data = []
        print(prop)
        for firm_history in history.firms_history:
            if not (hasattr(firm_history, prop)):
                continue
            line = getattr(firm_history, prop)
            data.append(Scatter(x=list(range(len(line))), y=list(line), name=firm_history.title))
        if data:
            plotly.offline.plot(figure_or_data={
                "data": data,
                "layout": Layout(
                        title=prop
                )
            }, filename='graphs/' + prop + '.html')
        data.clear()
        if hasattr(history.world_history, prop):
            line = getattr(history.world_history, prop)
            data.append(Scatter(x=list(range(len(line))), y=list(line), name=history.world_history.title))
            plotly.offline.plot(figure_or_data={
                "data": data,
                "layout": Layout(
                        title="world_" + prop
                )
            }, filename='graphs/world_' + prop + '.html')
