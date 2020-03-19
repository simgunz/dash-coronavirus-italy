import json
import urllib

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np
from scipy.optimize import curve_fit


def exponenial_func(x, a, b, c):
    return a*np.exp(-b*x)+c


########### Define your variables
color1='lightblue'
mytitle='Coronavirus casi totali'
tabtitle='Coronavirus'
myheading='Contagi coronavirus'
label1='Totale contagi'
githublink='https://github.com/simgunz/dash-coronavirus-italy'
sourceurl='https://github.com/pcm-dpc/COVID-19'

## Load the data
dataurl = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json"
data = urllib.request.urlopen(dataurl).read().decode()
dataj = json.loads(data)

y = [d['totale_casi'] for d in dataj]
x = list(range(len(y)))

popt, pcov = curve_fit(exponenial_func, np.array(x), np.array(y), p0=(1, 1e-6, 1))

xx = np.array(x)
yy = exponenial_func(xx, *popt)

########### Set up the chart
trace = go.Scatter(
    x = x,
    y = y,
    mode = 'markers'
)

trace2 = go.Scatter(
                  x=xx,
                  y=yy,
                  mode='lines',
                  marker=go.Marker(color='rgb(31, 119, 180)'),
                  name='Fit'
                  )

beer_data = [trace, trace2]
beer_fig = go.Figure(data=beer_data)


########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    html.H1(myheading),
    dcc.Graph(
        id='flyingdog',
        figure=beer_fig
    ),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A('Data Source', href=sourceurl),
    ]
)

if __name__ == '__main__':
    app.run_server()
