import plotly
from plotly.graph_objs import Scatter, Layout


class Visualiser:
    def plot(self, history, prop):
        data = []
        print(prop)
        for i, history in history:
            line = getattr(history, prop)
            data.append(Scatter(x=list(range(len(line))), y=list(line), name=history.title + " " + str(i)))
        plotly.offline.plot(figure_or_data={
            "data": data,
            "layout": Layout(
                title=prop
            )
        }, filename='graphs/' + prop + '.html')
