import json
import urllib
from datetime import datetime

import numpy as np
from scipy.optimize import curve_fit

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Define your variables
color1 = "lightblue"
mytitle = "Coronavirus casi totali"
tabtitle = "Coronavirus"
myheading = "Contagi coronavirus"
label1 = "Totale contagi"
githublink = "https://github.com/simgunz/dash-coronavirus-italy"
sourceurl = "https://github.com/pcm-dpc/COVID-19"

# Load the data
dataurl = ("https://raw.githubusercontent.com/pcm-dpc/"
           "COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json")
data = urllib.request.urlopen(dataurl).read().decode()
dataset = json.loads(data)

y_cases_total = [d["totale_casi"] for d in dataset]
days = list(range(len(y_cases_total)))
x_days = [
        datetime.strptime(report["data"], "%Y-%m-%d %H:%M:%S").strftime("%d %b")
        for report in dataset
    ]

# Initiate the app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = tabtitle

# Set up the layout
app.layout = html.Div(
    [
        dcc.Graph(id="total-cases"),
        dcc.Slider(
            id="day-slider",
            min=5,
            max=len(x_days),
            value=5,
            marks={i: day for i, day in enumerate(x_days)},
        ),
        html.Br(),
        html.A("Code on Github", href=githublink),
        html.Br(),
        html.A("Data Source", href=sourceurl),
    ]
)


def exponenial_func(x, a, b, c):
    return a * np.exp(b * x) + c


def fsigmoid(x, L, x0, k, b):
    y = L / (1 + np.exp(-k * (x - x0))) + b
    return y


@app.callback(Output("total-cases", "figure"), [Input("day-slider", "value")])
def create_total_cases(selected_day):
    traces = []
    traces.append(
        dict(
            x=x_days,
            y=y_cases_total,
            # text=df_by_continent['country'],
            mode="markers",
            opacity=0.7,
            marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
            name="Total cases",
        )
    )

    traces.append(
        dict(
            x=x_days[:selected_day],
            y=y_cases_total[:selected_day],
            # text=df_by_continent['country'],
            mode="markers",
            opacity=0.7,
            marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
            name="Dati usati per il fit",
        )
    )

    x_fit = np.array(days)
    y_fit = np.array(y_cases_total)
    popt, pcov = curve_fit(
        exponenial_func, x_fit[:selected_day], y_fit[:selected_day], p0=(1, 1e-6, 1)
    )

    xx = np.array(days)
    yy = exponenial_func(xx, *popt)

    traces.append(
        dict(
            x=[
                datetime.strptime(report["data"], "%Y-%m-%d %H:%M:%S").strftime("%d %b")
                for i, report in enumerate(dataset)
            ],
            y=yy,
            # text=df_by_continent['country'],
            mode="line",
            opacity=1,
            name="Fit esponenziale",
        )
    )
    p0 = [
        max(y_fit[:selected_day]),
        np.median(x_fit[:selected_day]),
        1,
        min(y_fit[:selected_day]),
    ]
    popt, pcov = curve_fit(
        fsigmoid, x_fit[:selected_day], y_fit[:selected_day], p0, method="dogbox"
    )
    yy = fsigmoid(xx, *popt)

    print(yy)

    traces.append(
        dict(
            x=[
                datetime.strptime(report["data"], "%Y-%m-%d %H:%M:%S").strftime("%d %b")
                for i, report in enumerate(dataset)
            ],
            y=yy,
            # text=df_by_continent['country'],
            mode="line",
            opacity=1,
            name="Fit sigmoide",
        )
    )

    return {
        "data": traces,
        "layout": dict(
            xaxis={"title": "Giorno"},
            yaxis={"title": "Casi totali"},
            margin={"l": 40, "b": 40, "t": 10, "r": 10},
            hovermode="closest",
            transition={"duration": 500},
        ),
    }


if __name__ == "__main__":
    app.run_server(debug=True)
