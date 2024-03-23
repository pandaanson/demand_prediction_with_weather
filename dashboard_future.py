
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json
import numpy as np
import os
from shapely.geometry import Point
from shapely import wkt
from datetime import date
import ast  # Import the ast module
from ast import literal_eval

# Get the current directory where your script is running
current_directory = os.getcwd()

# Construct the path to your resources folder dynamically
data_path = os.path.join(current_directory, 'web_page_data')


# Define file paths for saving
gdf_country_path = os.path.join(data_path, 'gdf_country.gpkg')
gdf_state_path = os.path.join(data_path, 'gdf_state.gpkg')
gdf_subregion_path = os.path.join(data_path, 'gdf_subregion.gpkg')

# Define paths for the GeoJSON files
country_geojson_path = os.path.join(data_path, 'country_centroids.csv')
state_geojson_path = os.path.join(data_path, 'state_centroids.csv')
rb_geojson_path = os.path.join(data_path, 'rb_centroids.csv')


# Function to read GeoJSON from a file
def read_geojson(file_path):
    with open(file_path) as f:
        return json.load(f)


# Read the GeoDataFrames
gdf_country = gpd.read_file(gdf_country_path)
gdf_state = gpd.read_file(gdf_state_path)
gdf_subregion = gpd.read_file(gdf_subregion_path)

gdf_country = gdf_country.to_crs(epsg=4326)
gdf_state = gdf_state.to_crs(epsg=4326)
gdf_subregion = gdf_subregion.to_crs(epsg=4326)

geojson_country = gdf_country.__geo_interface__
geojson_state = gdf_state.__geo_interface__
geojson_subregion = gdf_subregion.__geo_interface__


# Use pandas to read the CSV files
country_centroids_df = pd.read_csv(country_geojson_path)
state_centroids_df = pd.read_csv(state_geojson_path)
rb_centroids_df = pd.read_csv(rb_geojson_path)

# Function to convert a DataFrame with 'lon' and 'lat' columns to a GeoDataFrame
def df_to_gdf(df):
    # Create a GeoSeries from the 'lon' and 'lat' columns
    geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf

# Convert the DataFrames to GeoDataFrames
gdf_country_centroids = df_to_gdf(country_centroids_df)
gdf_state_centroids = df_to_gdf(state_centroids_df)
gdf_rb_centroids = df_to_gdf(rb_centroids_df)
weekday_map = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}

# Initialize the Dash app
app = dash.Dash(__name__)
server=app.server

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='usa-map', 
            config={'scrollZoom': False,'modeBarButtonsToRemove': ['zoom', 'zoomIn', 'zoomOut', 'pan']},
            style={'display': 'inline-block', 'width': '80%'}
        ),
        html.Div([
            html.H4("Select Breakdown:", style={'marginBottom': -20, 'marginTop': 0}), 
            dcc.RadioItems(
                id='map-toggle',
                options=[
                    {'label': 'Whole Country', 'value': 'country'},
                    {'label': 'By State', 'value': 'state'},
                    {'label': 'By Subregion', 'value': 'subregion'},
                ],
                value='country',  # Default value
                style={'padding': 20},
                inline=True
            ),
            html.H4("Select Scenario:", style={'marginBottom': -20, 'marginTop': 0}),
            dcc.RadioItems(
                id='scenario-toggle',
                options=[
                    {'label': 'Most extreme', 'value': 'rcp85hotter'},
                    {'label': 'Extreme', 'value': 'rcp85cooler'},
                    {'label': 'Mini extreme', 'value': 'rcp45hotter'},
                    {'label': 'Least extreme', 'value': 'rcp45cooler'},
                    {'label': 'Stable(unimplement)','value': 'stable'}
                ],
                value='rcp85hotter',  # Default value
                style={'padding': 20},
                inline=True
            ),
            # html.H4("Select Time for the map:", style={'marginBottom': 0, 'marginTop': 0}),
            # html.Div([
            # dcc.DatePickerRange(
            #     id='date-picker-range',
            #     min_date_allowed=date(2020, 1, 1),
            #     max_date_allowed=date(2100, 12, 31),
            #     start_date=date(2020, 1, 1),
            #     end_date=date(2100, 12, 31)
            # )
            # ]),
            html.Div([
                html.Div([
                    html.H4("Start Month:", style={'marginBottom': 0, 'marginTop': 0}),
                    dcc.Dropdown(
                        id='start-month-dropdown',
                        options=[{'label': month, 'value': month} for month in range(1, 13)],
                        value=1  # Default to January
                    ),
                    html.H4("Start Year:", style={'marginBottom': 0, 'marginTop': 0}),
                    dcc.Dropdown(
                        id='start-year-dropdown',
                        options=[{'label': year, 'value': year} for year in range(2020, 2101)],
                        value=2020  # Default to 2020
                    )
                ], style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H4("End Month:", style={'marginBottom': 0, 'marginTop': 0}),
                    dcc.Dropdown(
                        id='end-month-dropdown',
                        options=[{'label': month, 'value': month} for month in range(1, 13)],
                        value=12  # Default to December
                    ),
                    html.H4("End Year:", style={'marginBottom': 0, 'marginTop': 0}),
                    dcc.Dropdown(
                        id='end-year-dropdown',
                        options=[{'label': year, 'value': year} for year in range(2020, 2101)],
                        value=2100  # Default to 2100
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
            ]),
            html.H4("Choose region to inspect:", style={'marginBottom': 0, 'marginTop': 0}), 
            html.Div([dcc.Dropdown(id='graph-toggle',value='USA',  multi=False)]),
        ], style={'display': 'inline-block', 'width': '20%', 'verticalAlign': 'top'}),
    ]),
    # Div for line graph
    html.Div([
        dcc.Graph(id='line-graph'),  # Placeholder for the line graph
    ], style={'width': '100%','display': 'inline-block'}),  # Adjust width to 50% to share space equally

    html.Div([
        # Div for comparison graph and dropdowns
        html.Div([
            dcc.Graph(id='compare-graph'),  # Placeholder for the comparison graph
        ], style={'width': '55%', 'display': 'inline-block'}),  # Use 100% of the parent div width

        html.Div([
            # Div for Year dropdowns
            html.Div([
                html.H4("Choose Year Left:", style={'marginBottom': 0, 'marginTop': 0}),
                dcc.Dropdown(
                    id='year-dropdown-left',
                    options=[{'label': year, 'value': year} for year in range(2020, 2100)],
                    value=2020  # Default value
                ),
                html.H4("Choose Year Right:", style={'marginBottom': 0, 'marginTop': 0}),
                dcc.Dropdown(
                    id='year-dropdown-right',
                    options=[{'label': year, 'value': year} for year in range(2020, 2100)],
                    value=2021  # Default value
                ),
            ], style={'width': '100%', 'display': 'inline-block'}),  # Use 100% of the parent div width

            # Div for Day Type dropdowns
            html.Div([
                html.H4("Choose Day Type Left:", style={'marginBottom': 0, 'marginTop': 0}),
                dcc.Dropdown(
                    id='daytype-dropdown-left',
                    options=[{'label': daytype, 'value': daytype} for daytype in ['Weekday', 'Weekend']],
                    value='Weekday'  # Default value
                ),
                html.H4("Choose Day Type Right:", style={'marginBottom': 0, 'marginTop': 0}),
                dcc.Dropdown(
                    id='daytype-dropdown-right',
                    options=[{'label': daytype, 'value': daytype} for daytype in ['Weekday', 'Weekend']],
                    value='Weekday'  # Default value
                ),
            ], style={'width': '100%', 'display': 'inline-block'}),  # Use 100% of the parent div width

            # Div for Day Type dropdowns
            html.Div([
                html.H4("Choose Scenario Type Left:", style={'marginBottom': -20, 'marginTop': 0}),
                dcc.RadioItems(
                    id='scenario-toggle-left',
                    options=[
                        {'label': 'Most extreme', 'value': 'rcp85hotter'},
                        {'label': 'Extreme', 'value': 'rcp85cooler'},
                        {'label': 'Mini extreme', 'value': 'rcp45hotter'},
                        {'label': 'Least extreme', 'value': 'rcp45cooler'},
                        {'label': 'Stable(unimplement)','value': 'stable'}
                    ],
                    value='rcp85hotter',  # Default value
                    style={'padding': 20},
                    inline=True
                ),
                html.H4("Choose Scenario Type Right:", style={'marginBottom': -20, 'marginTop': 0}),
                dcc.RadioItems(
                    id='scenario-toggle-right',
                    options=[
                        {'label': 'Most extreme', 'value': 'rcp85hotter'},
                        {'label': 'Extreme', 'value': 'rcp85cooler'},
                        {'label': 'Mini extreme', 'value': 'rcp45hotter'},
                        {'label': 'Least extreme', 'value': 'rcp45cooler'},
                        {'label': 'Stable(unimplement)','value': 'stable'}
                    ],
                    value='rcp85hotter',  # Default value
                    style={'padding': 20},
                    inline=True
                ),
            ], style={'width': '100%', 'display': 'inline-block'}),  # Use 100% of the parent div width

            # Div for Region dropdowns
            html.Div([
                html.H4("Choose Region Left:", style={'marginBottom': 0, 'marginTop': 0}),
                dcc.Dropdown(id='region-left', value='USA', multi=False),
                html.H4("Choose Region Right:", style={'marginBottom': 0, 'marginTop': 0}),
                dcc.Dropdown(id='region-right', value='USA', multi=False),
            ], style={'width': '100%', 'display': 'inline-block'}),  # Use 100% of the parent div width
        ], style={'display': 'inline-block', 'width': '45%'}),  # Adjust width to 50% to share space equally
    ], style={'display': 'flex', 'flex-direction': 'row'}),  # Use flexbox for side-by-side layout
    html.Div([
        # Div for comparison graph and dropdowns
        html.Div([
            dcc.Graph(id='compare-graph-week'),  # Placeholder for the comparison graph
        ], style={'width': '55%', 'display': 'inline-block'}),  # Use 100% of the parent div width
    ], style={'display': 'flex', 'flex-direction': 'row'})  # Use flexbox for side-by-side layout

])

@app.callback(
    Output('usa-map', 'figure'),
    [
        Input('scenario-toggle', 'value'),
        Input('map-toggle', 'value'),
        Input('start-month-dropdown', 'value'),
        Input('start-year-dropdown', 'value'),
        Input('end-month-dropdown', 'value'),
        Input('end-year-dropdown', 'value')
    ]
)


def update_map(scenario_value,toggle_value,start_month,start_year,end_month,end_year):
    # Choose the correct DataFrame and title based on toggle_value
    if toggle_value == 'country':
        data = gdf_country
        geojson = geojson_country
        color_column = 'country'
        df_centroids=gdf_country_centroids
        # Define the columns to read from the CSV file
        columns_to_read = ['Year','Month', 'USA']
    elif toggle_value == 'state':
        data = gdf_state
        geojson = geojson_state
        color_column = 'state'
        df_centroids=gdf_state_centroids
        columns_to_read = ['Year','Month', 'Alabama', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
           'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
          'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
          'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
          'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
    else:  # Assuming 'subregion'
        data = gdf_subregion
        geojson = geojson_subregion
        color_column = 'rb'
        df_centroids=gdf_rb_centroids
        columns_to_read = ['Year','Month'] + [f'p{i}' for i in range(1, 135)]
    resources_path=os.path.join(current_directory, 'resources')
    file_path = os.path.join(resources_path, f'mock_{scenario_value}.csv')


    
    # Read only the selected columns from the CSV file
    df = pd.read_csv(file_path, usecols=columns_to_read)
    
    start_date = pd.Timestamp(year=start_year, month=start_month, day=1)
    end_date = pd.Timestamp(year=end_year, month=end_month, day=30)
    
    # Create a mask for the date range
    mask = (df['Year'] > start_year) | \
           ((df['Year'] == start_year) & (df['Month'] >= start_month)) & \
           (df['Year'] < end_year) | \
           ((df['Year'] == end_year) & (df['Month'] <= end_month))
    # Sum df vertically by column
    df_summed = df.drop(['Year', 'Month'], axis=1).sum().reset_index()
    df_summed.columns = ['region', 'demand']

    # Create a mapping from region to demand
    demand_mapping = df_summed.set_index('region')['demand'].to_dict()

    # Apply the mapping to create a new 'demand' column in 'data'
    data['demand'] = data[color_column].map(demand_mapping)
    # Use Plotly Express to create the choropleth map with a Mapbox base map
    fig = px.choropleth_mapbox(data, geojson=geojson, 
                               locations=data.index, 
                               color='demand',
                               color_continuous_scale=[(0, "green"), (1, "red")],
                               mapbox_style="carto-positron",
                               hover_data=[color_column,'demand'],
                               zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=0.5)

    # Update layout to fix the map view (disable zoom and pan)
    fig.update_layout(
        mapbox=dict(
            center={"lat": 37.0902, "lon": -95.7129},
            zoom=3,
            style="carto-positron"
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        title=f"Map by {toggle_value.title()}",
    )


    return fig

@app.callback(
    [Output('graph-toggle', 'options'),
     Output('graph-toggle', 'value')],
    [Input('map-toggle', 'value')]
)
def set_graph_toggle_options(selected_map_view):
    #print(f"Selected map view: {selected_map_view}")
    if selected_map_view == 'country':
        # Explicitly return 'USA' as the option
        options = [{'label': 'USA', 'value': 'USA'}]
        value='USA'
    elif selected_map_view == 'state':
        # Example state list; replace with your actual data or method to retrieve states
        options =[{'label': i, 'value': i} for i in state_centroids_df['state'].unique()]
        value='New York'
    elif selected_map_view == 'subregion':
        # Generate subregion options from 'p1' to 'p134'
        options = [{'label': f'p{i}', 'value': f'p{i}'} for i in range(1, 135)]
        value='p1'

    return options,value
@app.callback(
    [
        Output('region-left', 'options'),
        Output('region-right', 'options'),
        Output('region-left', 'value'),
        Output('region-right', 'value')
    ],
    [
        Input('map-toggle', 'value')
    ]
)
def set_region_options(selected_map_view):
    if selected_map_view == 'country':
        # Explicitly return 'USA' as the option
        options = [{'label': 'USA', 'value': 'USA'}]
        value='USA'
    elif selected_map_view == 'state':
        # Example state list; replace with your actual data or method to retrieve states
        options =[{'label': i, 'value': i} for i in state_centroids_df['state'].unique()]
        value='New York'
    elif selected_map_view == 'subregion':
        # Generate subregion options from 'p1' to 'p134'
        options = [{'label': f'p{i}', 'value': f'p{i}'} for i in range(1, 135)]
        value='p1'
    return options, options ,value , value
@app.callback(
    Output('compare-graph', 'figure'),
    [
        Input('year-dropdown-left', 'value'),
        Input('daytype-dropdown-left', 'value'),
        Input('scenario-toggle-left', 'value'),
        Input('region-left', 'value'),
        Input('year-dropdown-right', 'value'),
        Input('daytype-dropdown-right', 'value'),
        Input('scenario-toggle-right', 'value'),
        Input('region-right', 'value'),
    ]
)

def update_daily_compare_graph(year_left, daytype_left, scenario_left, region_left,
                 year_right, daytype_right, scenario_right, region_right):
    #Sample dr
    compare_df_path= os.path.join(data_path, 'mock_rcp85hotter_yearly_aggregated.csv')
    compare_df = pd.read_csv(compare_df_path)

    # Create the figure
    fig = go.Figure()

    # Hours array to use as x-axis
    hours = list(range(24))
    ## Left
    # Construct column names for mean, upper, and lower
    column_name_left_mean = f"{region_left}_mean"
    column_name_left_upper = f"{region_left}_upper"
    column_name_left_lower = f"{region_left}_lower"
    daytype_left

    # Assuming compare_df structure and that the row for the selected year and region exists
    row_left = compare_df[(compare_df['Year'] == year_left) & (compare_df['Weekend_or_Weekday']== daytype_left)]
    if not row_left.empty:
        left_mean = row_left[column_name_left_mean].values
        left_upper = row_left[column_name_left_upper].values
        left_lower = row_left[column_name_left_lower].values
        hours_left = row_left['Hour'].values

        # Plot mean
        fig.add_trace(go.Scatter(x=hours_left, y=left_mean, mode='lines', name='Left Mean', line=dict(color='blue')))
        # Plot upper and lower with fill
        fig.add_trace(go.Scatter(x=hours_left, y=left_upper, mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=hours_left, y=left_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,0,255,0.2)', showlegend=False))

    ## Right
    # Construct column names for mean, upper, and lower
    column_name_right_mean = f"{region_right}_mean"
    column_name_right_upper = f"{region_right}_upper"
    column_name_right_lower = f"{region_right}_lower"

    # Assuming compare_df structure and that the row for the selected year and region exists
    row_right = compare_df[(compare_df['Year'] == year_right) & (compare_df['Weekend_or_Weekday']== daytype_right)]
    if not row_right.empty:
        right_mean = row_right[column_name_right_mean].values
        right_upper = row_right[column_name_right_upper].values
        right_lower = row_right[column_name_right_lower].values
        hours_right = row_right['Hour'].values

        # Plot mean
        fig.add_trace(go.Scatter(x=hours_right, y=right_mean, mode='lines', name='Right Mean', line=dict(color='red')))
        # Plot upper and lower with fill
        fig.add_trace(go.Scatter(x=hours_right, y=right_upper, mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=hours_right, y=right_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(255,0,0,0.2)', showlegend=False))

    fig.update_layout(title=f'{daytype_left} of {region_left} in {year_left} base on {scenario_left} <br>vs {daytype_right} of {region_right} in {year_right} base on {scenario_right}', xaxis_title='Hour of Day', yaxis_title='Hourly Demand(Mwh)', xaxis=dict(range=[0, 23]))

    return fig


@app.callback(
    Output('compare-graph-week', 'figure'),
    [
        Input('year-dropdown-left', 'value'),
        Input('daytype-dropdown-left', 'value'),
        Input('scenario-toggle-left', 'value'),
        Input('region-left', 'value'),
        Input('year-dropdown-right', 'value'),
        Input('daytype-dropdown-right', 'value'),
        Input('scenario-toggle-right', 'value'),
        Input('region-right', 'value'),
    ]
)

def update_weekly_compare_graph(year_left, daytype_left, scenario_left, region_left,
                 year_right, daytype_right, scenario_right, region_right):
    #Sample dr

    compare_weekly_df_path= os.path.join(data_path, 'mock_rcp85hotter_weekly.csv')
    compare_weekly_df = pd.read_csv(compare_weekly_df_path)
    # Create the figure
    fig = go.Figure()

    # Hours array to use as x-axis
    hours = list(range(7))
    ## Left
    try:
        # Construct column names for mean, upper, and lower
        column_name_left_mean = f"{region_left}_mean"
        column_name_left_upper = f"{region_left}_upper"
        column_name_left_lower = f"{region_left}_lower"

        # Assuming compare_df structure and that the row for the selected year and region exists
        row_left = compare_weekly_df[(compare_weekly_df['Year'] == year_left)]
        if not row_left.empty:
            left_mean = row_left[column_name_left_mean].values
            left_upper = row_left[column_name_left_upper].values
            left_lower = row_left[column_name_left_lower].values
            weekdays_left = row_left['weekday'].map(weekday_map).values

            # Plot mean
            fig.add_trace(go.Scatter(x=weekdays_left , y=left_mean, mode='lines', name='Left Mean', line=dict(color='blue')))
            # Plot upper and lower with fill
            fig.add_trace(go.Scatter(x=weekdays_left , y=left_upper, mode='lines', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=weekdays_left , y=left_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(0,0,255,0.2)', showlegend=False))

        ## Right
        # Construct column names for mean, upper, and lower
        column_name_right_mean = f"{region_right}_mean"
        column_name_right_upper = f"{region_right}_upper"
        column_name_right_lower = f"{region_right}_lower"

        # Assuming compare_df structure and that the row for the selected year and region exists
        row_right = compare_weekly_df[(compare_weekly_df['Year'] == year_right)]
        if not row_right.empty:
            right_mean = row_right[column_name_right_mean].values
            right_upper = row_right[column_name_right_upper].values
            right_lower = row_right[column_name_right_lower].values
            weekdays_right = row_left['weekday'].map(weekday_map).values


            # Plot mean
            fig.add_trace(go.Scatter(x=weekdays_right, y=right_mean, mode='lines', name='Right Mean', line=dict(color='red')))
            # Plot upper and lower with fill
            fig.add_trace(go.Scatter(x=weekdays_right, y=right_upper, mode='lines', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=weekdays_right, y=right_lower, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(255,0,0,0.2)', showlegend=False))
    except Exception as e:
        print(e)
    fig.update_layout(title=f'Week of {region_left} in {year_left} base on {scenario_left} <br>vs Week of {region_right} in {year_right} base on {scenario_right}',xaxis_title='Week Day', yaxis_title='Daily Average demand(Mwh)', xaxis=dict(range=[0, 6]))

    return fig

@app.callback(
    Output('line-graph', 'figure'),
    [
        Input('scenario-toggle', 'value'),
        Input('graph-toggle', 'value'),
        Input('start-month-dropdown', 'value'),
        Input('start-year-dropdown', 'value'),
        Input('end-month-dropdown', 'value'),
        Input('end-year-dropdown', 'value')
    ]
)
def update_line_graph(scenario_value, graph_value, start_month, start_year, end_month, end_year):

    scenarios = ['rcp85hotter']#, 'rcp85cooler', 'rcp45hotter', 'rcp45cooler']
    resources_path = os.path.join(current_directory, 'resources')

    # Create the figure outside of the loop, so all lines are on the same graph
    fig = go.Figure()

    for scenario_value in scenarios:
        # Construct the file path for the current scenario
        file_path = os.path.join(resources_path, f'mock_{scenario_value}.csv')

        # Define the columns to read from the CSV file
        columns_to_read = ['Year', 'Month', graph_value]

        # Read only the selected columns from the CSV file
        df = pd.read_csv(file_path, usecols=columns_to_read)

        # Create a datetime column from 'Year' and 'Month' for filtering
        df['time'] = pd.to_datetime(df.assign(Day=1)[['Year', 'Month', 'Day']])
        
        # Create start and end date Timestamps
        start_date = pd.Timestamp(year=start_year, month=start_month, day=1)
        end_date = pd.Timestamp(year=end_year, month=end_month, day=1)
        
        # Filter the data based on the selected date range
        mask = (df['time'] >= start_date) & (df['time'] <= end_date)
        filtered_df = df.loc[mask]
        
        # Extract the data for plotting
        x_data = filtered_df['time']
        y_data = filtered_df[graph_value]

        # Add the line trace for the current scenario
        fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines', name=scenario_value))

    # Dynamically set the title to indicate a comparison
    title_text = f"Comparison of Scenarios for {graph_value}"
    fig.update_layout(title=title_text)

    # Display the figure
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)