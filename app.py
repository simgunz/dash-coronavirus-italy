import json
import urllib

import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from helpers import fit_data, exponenial_func, logistic_func, day_labels

# Define your variables
fit_day_count = 30

mytitle = "Coronavirus casi totali"
tabtitle = "Coronavirus"
myheading = "Contagi coronavirus"
label1 = "Totale contagi"
githublink = "https://github.com/simgunz/dash-coronavirus-italy"
sourceurl = "https://github.com/pcm-dpc/COVID-19"
colors = [
    "#1f77b4",  # muted blue
    "#ff7f0e",  # safety orange
    "#2ca02c",  # cooked asparagus green
    "#d62728",  # brick red
    "#9467bd",  # muted purple
    "#8c564b",  # chestnut brown
    "#e377c2",  # raspberry yogurt pink
    "#7f7f7f",  # middle gray
    "#bcbd22",  # curry yellow-green
    "#17becf",  # blue-teal
]

# Load the data
dataurl = (
    "https://raw.githubusercontent.com/pcm-dpc/"
    "COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"
)
data = urllib.request.urlopen(dataurl).read().decode()
dataset = json.loads(data)

y_cases_total = [d["totale_casi"] for d in dataset]
day_count = len(y_cases_total)
x_days = day_labels(dataset[0]["data"], fit_day_count)
x_days_index = list(range(len(x_days)))

# Initiate the app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__)
server = app.server
app.title = tabtitle

# Set up the layout
app.layout = html.Div(
    [
        dcc.Slider(
            id="day-slider",
            min=5,
            max=day_count,
            value=day_count - 5,
            marks={i: day for i, day in enumerate(x_days[:day_count])},
        ),
        dcc.Graph(id="total-cases",),
        html.Br(),
        html.Div(id="total-cases-errors"),
        html.Br(),
        html.A("Code on Github", href=githublink),
        html.Br(),
        html.A("Data Source", href=sourceurl),
    ]
)


@app.callback(
    [Output("total-cases", "figure"), Output("total-cases-errors", "children")],
    [Input("day-slider", "value")],
)
def create_total_cases(selected_day_index):
    traces = []
    errors = []
    data_used_for_fit = dict(
        x=x_days[:selected_day_index],
        y=y_cases_total[:selected_day_index],
        # text=df_by_continent['country'],
        mode="markers",
        opacity=1,
        marker={
            "size": 15,
            "color": colors[0],
            "line": {"width": 0.5, "color": "white"},
        },
        name="Data used for fit",
    )
    data_not_used_for_fit = dict(
        x=x_days[selected_day_index:day_count],
        y=y_cases_total[selected_day_index:day_count],
        # text=df_by_continent['country'],
        mode="markers",
        opacity=1,
        marker={
            "size": 15,
            "color": colors[1],
            "line": {"width": 0.5, "color": "white"},
        },
        name="Data",
    )

    if selected_day_index <= 18:
        try:
            p0 = (1, 1e-6, 1)
            y_exp = fit_data(
                exponenial_func,
                x_days_index,
                y_cases_total,
                p0,
                selected_day_index,
                fit_day_count,
            )
            traces.append(
                dict(
                    x=x_days,
                    y=y_exp,
                    # text=df_by_continent['country'],
                    mode="line",
                    line={"color": colors[2]},
                    opacity=1,
                    name="Exponential fit",
                )
            )
        except RuntimeError:
            errors.append("Exponential fit failed")
    else:
        try:
            p0 = (
                max(y_cases_total),
                np.median(np.arange(day_count)),
                1,
                min(y_cases_total),
            )
            y_logi = fit_data(
                logistic_func,
                x_days_index,
                y_cases_total,
                p0,
                selected_day_index,
                fit_day_count,
            )
            traces.append(
                dict(
                    x=x_days,
                    y=y_logi,
                    # text=df_by_continent['country'],
                    mode="line",
                    line={"color": colors[3]},
                    opacity=1,
                    name="Logistic fit",
                )
            )
        except RuntimeError:
            errors.append("Logistic fit failed")

    traces += [data_used_for_fit, data_not_used_for_fit]

    figure = {
        "data": traces,
        "layout": dict(
            # xaxis={"rangeslider": {"visible": False}},
            yaxis={"title": "Total number of cases"},
            margin={"l": 40, "b": 40, "t": 10, "r": 10},
            hovermode="closest",
            transition={"duration": 0},
        ),
    }
    return figure, "<br />".join(errors)


if __name__ == "__main__":
    app.run_server(debug=True)
