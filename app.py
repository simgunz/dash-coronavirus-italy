import json
import urllib
from datetime import timedelta, datetime

import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from helpers import fit_data, exponenial_func, logistic_func, day_labels, nearest

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

controls = dbc.Card(
    dbc.FormGroup(
        [
            dbc.Label("Days used for fit", html_for="day-slider"),
            dcc.Slider(
                id="day-slider",
                min=5,
                max=day_count,
                value=day_count,
                step=1,
                marks={i: x_days_str[i] for i in range(0, len(x_days_str), 5)},
            ),
        ]
    ),
    body=True,
)

display = [
    html.H2("Total number of cases", className="text-center"),
    dcc.Graph(id="total-cases"),
    html.Div(id="total-cases-errors"),
]

footer = (
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
)

app.layout = html.Div(
    [
        dbc.Jumbotron(
            html.H1("Coronavirus forecast Italy", className="display-4 text-center")
        ),
        dbc.Container(
            [
                dbc.Row([dbc.Col(display, md=12)]),
                dbc.Row([dbc.Col(controls, md=12)]),
                dbc.Row([dbc.Col(footer, md=12)]),
            ],
            fluid=False,
        ),
    ]
)


@app.callback(
    [Output("total-cases", "figure"), Output("total-cases-errors", "children")],
    [Input("day-slider", "value"), Input("total-cases", "relayoutData")],
    [State("total-cases", "figure")],
)
def create_total_cases(selected_day_index, relayoutData, prev_figure):
    traces = []
    errors = []
    visible_state = {}
    if prev_figure:
        # Set default xaxis range to existing one
        xaxis_range = prev_figure["layout"]["xaxis"]["range"]
        # Get trace visibility state
        for i in prev_figure["data"]:
            visible = i["visible"] if "visible" in i.keys() else True
            visible_state[i["name"]] = visible
    else:
        # Set xaxis defaults when figure created for the first time
        xmin = str(x_days[0] - timedelta(days=1))
        xmax = str(x_days[day_count + 10])
        xaxis_range = [xmin, xmax]

    # Define xaxis range
    if relayoutData:
        if "xaxis.autorange" in relayoutData and relayoutData["xaxis.autorange"]:
            # Triggered when the user double clicks on the graph
            xmin = str(x_days[0] - timedelta(days=1))
            xmax = str(x_days[day_count + 10])
            xaxis_range = [xmin, xmax]
        elif "xaxis.range[0]" in relayoutData:
            # Triggered by user zooming
            xaxis_range = [
                relayoutData["xaxis.range[0]"],
                relayoutData["xaxis.range[1]"],
            ]

    # Get maximum of yaxis
    ridx = nearest(x_days, xaxis_range[1])
    yidx = min(ridx, len(y_cases_total) - 1)
    yaxis_max = y_cases_total[yidx]

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
        if (
            "Exponential fit" not in visible_state
            or visible_state["Exponential fit"] is True
        ):
            yaxis_max = np.maximum(yaxis_max, y_exp[ridx])
    except RuntimeError:
        errors.append("Exponential fit failed")

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
        if "Logistic fit" not in visible_state or visible_state["Logistic fit"] is True:
            yaxis_max = np.maximum(yaxis_max, y_logi[ridx])
    except RuntimeError:
        errors.append("Logistic fit failed")

    traces += [data_used_for_fit, data_not_used_for_fit]

    figure = {
        "data": traces,
        "layout": dict(
            xaxis={
                "type": "date",
                "range": xaxis_range,
                "rangeslider": {"visible": True, "range": [x_days[0], x_days[-1]]},
            },
            yaxis={"range": [0, 1.1 * yaxis_max]},
            margin={"l": 40, "b": 40, "t": 50, "r": 10},
            hovermode="closest",
            transition={"duration": 0},
            legend={"x": 0.03, "y": 0.98},
        ),
    }

    # Restore visibility state
    for j in figure["data"]:
        if j["name"] in visible_state:
            j["visible"] = visible_state[j["name"]]

    return figure, "<br />".join(errors)


if __name__ == "__main__":
    app.run_server(debug=True)
