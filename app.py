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
dataurl = (
    "https://raw.githubusercontent.com/pcm-dpc/"
    "COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"
)
data = urllib.request.urlopen(dataurl).read().decode()
dataset = json.loads(data)

y_cases_total = [d["totale_casi"] for d in dataset]
x_days = [
    datetime.strptime(report["data"], "%Y-%m-%d %H:%M:%S").strftime("%d %b")
    for report in dataset
]
x_days_index = list(range(len(x_days)))

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
        html.Div(id="total-cases-errors"),
        html.Br(),
        html.A("Code on Github", href=githublink),
        html.Br(),
        html.A("Data Source", href=sourceurl),
    ]
)


def exponenial_func(x, a, b, c):
    return a * np.exp(b * x) + c


def logistic_func(x, L, x0, k, b):
    return L / (1 + np.exp(-k * (x - x0))) + b


def fit_data(fit_func, x, y, fit_point_count, p0):
    x_array = np.array(x)
    y_array = np.array(y)
    x_fit = x_array[:fit_point_count]
    y_fit = y_array[:fit_point_count]
    popt, pcov = curve_fit(fit_func, x_fit, y_fit, p0=p0)
    y_fit = fit_func(x_array, *popt)
    return y_fit


@app.callback(
    [Output("total-cases", "figure"), Output("total-cases-errors", "children")],
    [Input("day-slider", "value")],
)
def create_total_cases(selected_day):
    errors = []
    data_used_for_fit = dict(
        x=x_days[:selected_day],
        y=y_cases_total[:selected_day],
        # text=df_by_continent['country'],
        mode="markers",
        opacity=0.7,
        marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
        name="Data used for fit",
    )
    data_not_used_for_fit = dict(
        x=x_days[selected_day:],
        y=y_cases_total[selected_day:],
        # text=df_by_continent['country'],
        mode="markers",
        opacity=0.7,
        marker={"size": 15, "line": {"width": 0.5, "color": "white"}},
        name="Data",
    )
    traces = [data_used_for_fit, data_not_used_for_fit]

    try:
        y_exp = fit_data(
            exponenial_func, x_days_index, y_cases_total, selected_day, p0=(1, 1e-6, 1)
        )
        traces.append(
            dict(
                x=x_days,
                y=y_exp,
                # text=df_by_continent['country'],
                mode="line",
                opacity=1,
                name="Exponential fit",
            )
        )
    except RuntimeError:
        errors.append("Exponential fit failed")

    try:
        p0 = (
            max(y_cases_total),
            np.median(np.arange(len(x_days))),
            1,
            min(y_cases_total),
        )
        y_logi = fit_data(
            logistic_func, x_days_index, y_cases_total, selected_day, p0=p0
        )
        traces.append(
            dict(
                x=x_days,
                y=y_logi,
                # text=df_by_continent['country'],
                mode="line",
                opacity=1,
                name="Logistic fit",
            )
        )
    except RuntimeError:
        errors.append("Logistic fit failed")

    figure = {
        "data": traces,
        "layout": dict(
            # xaxis={"title": "Giorno"},
            # yaxis={"title": "Casi totali"},
            margin={"l": 40, "b": 40, "t": 10, "r": 10},
            hovermode="closest",
            transition={"duration": 0},
        ),
    }
    return figure, "<br />".join(errors)


if __name__ == "__main__":
    app.run_server(debug=True)
