import json
import urllib
from datetime import timedelta

import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from helpers import fit_data, exponenial_func, logistic_func, day_labels

# Define your variables
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
forcast_days = 30
fit_day_count = day_count + forcast_days
x_days = day_labels(dataset[0]["data"], fit_day_count)
x_days_str = day_labels(dataset[0]["data"], fit_day_count, as_str=True)[:day_count]
x_days_index = list(range(len(x_days)))

# Initiate the app

# Meta tags for viewport responsiveness
meta_viewport = {
    "name": "viewport",
    "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
}

app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[meta_viewport]
)
server = app.server
app.title = tabtitle

# Set up the layout
app.layout = html.Div(
    [
        dbc.Jumbotron(
            html.H1("Coronavirus forecast Italy", className="display-3 text-center"),
        ),
        dbc.Container(
            [
                html.Div(
                    [
                        html.H1("Total number of cases", className="text-center"),
                        dcc.Graph(id="total-cases"),
                    ],
                    style={"margin-top": "50px"},
                ),
                html.Div(
                    [
                        html.Div("Days used for fit:"),
                        dcc.Slider(
                            id="day-slider",
                            min=5,
                            max=day_count,
                            value=day_count,
                            step=1,
                            marks={
                                i: x_days_str[i] for i in range(0, len(x_days_str), 5)
                            },
                        ),
                    ],
                    style={"margin-bottom": "50px"},
                ),
                html.Div(id="total-cases-errors"),
            ]
        ),
        html.Footer(
            dbc.Container(
                [
                    html.A("Code on Github", href=githublink),
                    html.Br(),
                    html.A("Data Source", href=sourceurl),
                ],
                className="text-white",
            ),
            className="page-footer font-small pt-4",
        ),
    ]
)


@app.callback(
    [Output("total-cases", "figure"), Output("total-cases-errors", "children")],
    [Input("day-slider", "value"), Input("total-cases", "relayoutData")],
)
def create_total_cases(selected_day_index, relayoutData):
    traces = []
    errors = []
    data_used_for_fit = dict(
        x=x_days[:selected_day_index],
        y=y_cases_total[:selected_day_index],
        # text=df_by_continent['country'],
        mode="markers",
        opacity=1,
        marker={
            "size": 10,
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
            "size": 10,
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

    if "xaxis.range" in relayoutData:
        xaxis_range = relayoutData["xaxis.range"]
    else:
        xaxis_range = [x_days[0] - timedelta(days=1), x_days[day_count + 10]]

    figure = {
        "data": traces,
        "layout": dict(
            xaxis={
                "type": "date",
                "range": xaxis_range,
                "rangeslider": {"visible": True, "range": [x_days[0], x_days[-1]]},
            },
            yaxis={"range": [0, 200000]},
            margin={"l": 40, "b": 40, "t": 50, "r": 10},
            hovermode="closest",
            transition={"duration": 0},
            legend={"x": 0.03, "y": 0.98},
        ),
    }
    return figure, "<br />".join(errors)


if __name__ == "__main__":
    app.run_server(debug=True)
