######################################################################################
# GazepointAPI.py - Example Client
# Written in 2013 by Gazepoint www.gazept.com
#
# To the extent possible under law, the author(s) have dedicated all copyright 
# and related and neighboring rights to this software to the public domain worldwide. 
# This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along with this 
# software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
######################################################################################

import socket
import dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

X = deque(maxlen=20)
X.append(1)
Y = deque(maxlen=20)
Y.append(85)


app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)

# Host machine IP
HOST = '172.28.96.1'
# Gazepoint Port
PORT = 4242
ADDRESS = (HOST, PORT)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDRESS)

# s.send(str.encode('<SET ID="ENABLE_SEND_CURSOR" STATE="1" />\r\n'))
# s.send(str.encode('<SET ID="ENABLE_SEND_POG_FIX" STATE="1" />\r\n'))
# s.send(str.encode('<SET ID="ENABLE_SEND_GSR" STATE="1"/>\r\n'))
s.send(str.encode('<SET ID="ENABLE_SEND_HR" STATE="1"/>\r\n'))
# s.send(str.encode('<SET ID="ENABLE_SEND_HR_PULSE" STATE="1"/>\r\n'))
s.send(str.encode('<SET ID="ENABLE_SEND_DATA" STATE="1" />\r\n'))


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    rxdat = s.recv(1024)    
    response = bytes.decode(rxdat)
    meaningful_response = response[response.rindex("HR=") : response.rindex("HR=") + 10]
    start_quote = str(meaningful_response).index('"')
    end_quote = meaningful_response[start_quote + 1:].index('"')
    in_between = int(meaningful_response[start_quote + 1: start_quote + end_quote + 1])
    X.append(X[-1] + 1)
    Y.append(in_between)

    data = go.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(50, min(Y)),max(85, max(Y))]))}



if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8080')
