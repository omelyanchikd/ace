import plotly
from plotly.graph_objs import Scatter, Layout


class Visualiser:
    def plot(self, histories, prop):
        data = []
        print(prop)
        for i, history in enumerate(histories):
            line = getattr(history, prop)
            data.append(Scatter(x=list(range(len(line))), y=list(line), name="Firm " + str(i)))
        plotly.offline.plot(figure_or_data={
            "data": data,
            "layout": Layout(
                title=prop
            )
        }, filename=prop + '.html')
