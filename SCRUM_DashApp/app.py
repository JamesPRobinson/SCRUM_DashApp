from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

import Data.UpdateData_Asana as Asana

import requests


today = dt.today().strftime('%Y-%m-%d')
df = pd.read_csv("/home/JPR17/mysite/Data/AsanaData.csv", parse_dates=["Date"])

Values = Asana.get_sprint_data(today)

ValueFrame = pd.DataFrame({'Date': [Values['Date']], 'CompletedTasks': [Values['CompletedTasks']],
                  'RemainingTasks': [Values['RemainingTasks']], 'RemainingEffort': [Values['RemainingEffort']]})
ValueFrame['Date'] = pd.to_datetime(ValueFrame['Date'])

if df["Date"].iloc[-1] != today: # New day, new row of data
    ValueFrame.to_csv("/home/JPR17/mysite/Data/AsanaData.csv", header=False, index=False, mode='a')
    df = pd.read_csv("/home/JPR17/mysite/Data/AsanaData.csv")

elif not df.iloc[-1].equals(other = ValueFrame.iloc[-1]): # New row for data updated over the course of the day
    df.iloc[-1] = ValueFrame.iloc[-1]
    df['Date'] = pd.to_datetime(df['Date'])
    df.to_csv("/home/JPR17/mysite/Data/AsanaData.csv",date_format='%Y-%m-%d', index=False, mode='w')
    df = pd.read_csv("/home/JPR17/mysite/Data/AsanaData.csv")

# ------------------------------------------------------------------------------
# Import and clean data (importing csv into pandas)

df['Date'] = pd.to_datetime(df['Date'])
DATE_MIN, DATE_MAX = df["Date"].iloc[0], df["Date"].iloc[-1]
df.set_index('Date', inplace=True)

# ------------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([html.Div([
    dcc.DatePickerRange(
        id='my-date-picker-range',  # ID to be used for callback
        calendar_orientation='horizontal',  # vertical or horizontal
        day_size=39,  # size of calendar image. Default is 39
        end_date_placeholder_text="End Date",  # text that appears when no end date chosen
        with_portal=False,  # if True calendar will open in a full screen overlay portal
        first_day_of_week=0,  # Display of calendar when open (0 = Sunday)
        reopen_calendar_on_clear=True,
        is_RTL=False,  # True or False for direction of calendar
        clearable=True,  # whether or not the user can clear the dropdown
        number_of_months_shown=1,  # number of months shown when calendar is open
        min_date_allowed=DATE_MIN,  # minimum date allowed on the DatePickerRange component
        max_date_allowed=DATE_MAX,  # maximum date allowed on the DatePickerRange component
        initial_visible_month=DATE_MAX,  # the month initially presented when the user opens the calendar
        start_date=DATE_MIN,
        end_date=DATE_MAX,
        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
        minimum_nights=2,  # minimum number of days between start and end date

        # These parameters are about memory, what dates the browser needs to remember
        persistence=True,
        persisted_props=['start_date'],
        persistence_type='session',  # session, local, or memory. Default is 'local'

        updatemode='singledate'  # singledate or bothdates. Determines when callback is triggered
    ),

    html.H3("Asana Data", style={'textAlign': 'center'}),
    dcc.Graph(id='mymap')
]),
    html.Div([
        html.Button('Show Burndown', id='button-burndown', n_clicks=0, style={'border-radius': '2px;'})])
])


@app.callback(
    Output('mymap', 'figure'),
    [dash.dependencies.Input('button-burndown', 'n_clicks')],
    [Input('my-date-picker-range', 'start_date'),
     Input('my-date-picker-range', 'end_date')]
)
def update_output(n_clicks, start_date, end_date):
    # print("Start date: " + start_date)
    # print("End date: " + end_date)
    dff = df.loc[start_date:end_date]

    # print(dff[:5])
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Scatter(x=dff.index, y=dff["RemainingEffort"], name="Remaining Effort"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=dff.index, y=dff["RemainingTasks"], name="Remaining Tasks"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(
            x=dff.index,
            y=dff["CompletedTasks"],
            name="Completed Tasks"
        ))
    # Add figure title
    fig.update_layout(
        title_text="Asana Tasks"
    )
    if n_clicks % 2 != 0:
        max_effort = dff["RemainingEffort"].iloc[0]
        regression = list(reversed(np.linspace(0, max_effort, len(dff.index)).tolist()))
        fig.add_trace(go.Scatter(x=dff.index, y=regression, name="Ideal Burndown"), secondary_y=True)
    # Set x-axis title
    fig.update_xaxes(title_text="Tasks Completed")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Effort</b> Remaining", secondary_y=True)
    fig.update_yaxes(title_text="<b>Tasks</b> Remaining", secondary_y=False)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=True)
