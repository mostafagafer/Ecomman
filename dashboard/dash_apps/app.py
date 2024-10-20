import dash
from dash import html, dcc
# from dash import dash_table  # Updated import
# from django_plotly_dash import DjangoDash

# # Initialize the Dash app
# app = DjangoDash('SimpleTableApp')

# # Dummy data
# data = [
#     {"Name": "Alice", "Age": 25, "Location": "New York"},
#     {"Name": "Bob", "Age": 30, "Location": "Paris"},
#     {"Name": "Charlie", "Age": 35, "Location": "Berlin"}
# ]

# # Define layout
# app.layout = html.Div([
#     html.H1('Simple Table Example'),
#     dash_table.DataTable(  # Updated usage
#         columns=[{"name": i, "id": i} for i in data[0].keys()],
#         data=data
#     )
# ])


# second
# import dash
# from dash import html, dcc
# from dash.dependencies import Input, Output
# import plotly.graph_objs as go
# from django_plotly_dash import DjangoDash

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']



# app = DjangoDash('SimpleTableApp', external_stylesheets=external_stylesheets)


# app.layout = html.Div([
#     html.H1('Square Root Slider Graph'),
#     dcc.Graph(id='slider-graph', animate=True, style={"backgroundColor": "#1a2d46", 'color': '#ffffff'}),
#     dcc.Slider(
#         id='slider-updatemode',
#         marks={i: '{}'.format(i) for i in range(20)},
#         max=20,
#         value=2,
#         step=1,
#         updatemode='drag',
#     ),

#     dcc.Checklist(
#     ['New York City', 'Montréal', 'San Francisco'],
# ),

#     html.Div([
#     # dcc.Dropdown(['NYC', 'MTL', 'SF'], 'NYC', id='demo-dropdown'),
#     # dcc.Dropdown(['New York City', 'Montreal', 'San Francisco'], 'Montreal'),
#     dcc.Dropdown(['New York City', 'Montreal', 'Paris', 'London', 'Amsterdam', 'Berlin', 'Rome'],
#                 multi=True ,
#                 id='height-example-dropdown',
#                 searchable=True),
#     html.Div(id='dd-output-container')
# ]),

# # Slider
# html.Div([
#     dcc.RangeSlider(0, 20, 1, value=[5, 15], id='my-range-slider'),
#     html.Div(id='slider-output-container')
# ])
# ])


# @app.callback(
#                Output('slider-graph', 'figure'),
#               [Input('slider-updatemode', 'value')])
# def display_value(value):


#     x = []
#     for i in range(value):
#         x.append(i)

#     y = []
#     for i in range(value):
#         y.append(i*i)

#     graph = go.Scatter(
#         x=x,
#         y=y,
#         name='Manipulate Graph'
#     )
#     layout = go.Layout(
#         paper_bgcolor='#27293d',
#         plot_bgcolor='rgba(0,0,0,0)',
#         xaxis=dict(range=[min(x), max(x)]),
#         yaxis=dict(range=[min(y), max(y)]),
#         font=dict(color='white'),

#     )
#     return {'data': [graph], 'layout': layout}

# @app.callback(
#     Output('dd-output-container', 'children'),
#     Input('demo-dropdown', 'value')
# )
# def update_output(value):
#     return f'You have selected {value}'

# @app.callback(
#     Output('slider-output-container', 'children'),
#     Input('my-slider', 'value'))
# def update_output(value):
#     return 'You have selected "{}"'.format(value)

import dash
from dash import html, dcc, callback
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import copy

from django_plotly_dash import DjangoDash



def plot_dashboard(data):
    df = pd.DataFrame(data)
    # Check the DataFrame columns after creation
    # print("DataFrame columns in plot_dashboard:", df.columns)
    # print("Sample data:\n", df.head())

    df['Category'] = df['Category'].astype(str)
    df['Subcategory'] = df['Subcategory'].astype(str)
    df['Product'] = df['Product'].astype(str)
    df['Brand'] = df['Brand'].astype(str)
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    # Generate monthly marks
    date_marks = {
        int(df['scraped_at'].min().timestamp()): df['scraped_at'].min().strftime('%Y-%m-%d'),
        int(df['scraped_at'].max().timestamp()): df['scraped_at'].max().strftime('%Y-%m-%d')
    }




    app = DjangoDash('OPPS_Line', external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

    # app.layout = html.Div(
    #     [
    #         html.Div(
    #             [
    #                 html.Div(
    #                     [
    #                         html.H5("Category"),
    #                         dcc.Dropdown(
    #                             id="category",
    #                             options=[{"label": i, "value": i} for i in sorted(df["Category"].unique())],
    #                             value=None
    #                         ),
    #                         html.H5("Subcategory"),
    #                         dcc.Dropdown(
    #                             id="subcategory",
    #                             options=[{"label": i, "value": i} for i in sorted(df["Subcategory"].unique())],
    #                             value=None
    #                         ),
    #                         html.H5("Product"),
    #                         dcc.Dropdown(
    #                             id="product",
    #                             options=[],
    #                             value=None,
    #                             multi=True

    #                         ),
    #                     ],
    #                     className='col-md-4',
    #                 style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'},
    #                 ),
    #                 html.Div(
    #                     [
    #                         dcc.Graph(id="line"),
    #                     ],
    #                     className='col-md-8',
    #                                         style={'width': '66%', 'display': 'inline-block', 'verticalAlign': 'top'},

    #                 ),
    #             ],
    #             className='row',
    #                         style={'display': 'flex', 'flexWrap': 'wrap'},

    #         ),
    #     ],
    #     className='container-fluid',
    # )

    # app.layout = html.Div(
    #     [ html.Div( [ 
    # html.Div( [  
    #     html.Div( [  
    #         html.Div( [ 
    #                     html.H5("Category",
    #                         className='pt-4',),
    #                     dcc.Dropdown(
    #                         id="category",
    #                         options=[{"label": i, "value": i} for i in sorted(df["Category"].unique())],
    #                         value=None,
    #                     ),
    #                     html.H5("Subcategory",
    #                         className='pt-4'),
    #                     dcc.Dropdown(
    #                         id="subcategory",
    #                         options=[{"label": i, "value": i} for i in sorted(df["Subcategory"].unique())],
    #                         value=None),
    #                     html.H5("Product",
    #                         className='pt-4'),
    #                     dcc.Dropdown(
    #                         id="product",
    #                         options=[],
    #                         value=None,
    #                         multi=True),
    #         ],className='card-body p-3' ),
    #     ],className='card z-index-2' ),
    # ],className='container-fluid')
    # ,
    # html.Div( [ 
    #     html.Div( [  
    #             html.Div( [ 
    #                 html.Div( [  
    #                     html.H4("Online Precie Performance Score Over Time (Grouped by 6-hour Intervals)"),
    #                 ],className='card-header pb-0' ),
    #                 html.Div( [  
    #                     dcc.Graph(id="line"),
    #                 ],className='card-body p-3' ),
    #         ],className='card-body p-3' ),
    #     ],className='card z-index-2' ),
    # ],className='container-fluid'),
    # ],className='row mt-4')
    # ],className='container-fluid')
    app.layout = html.Div(
        [
            html.Div([ 
                html.Div([  
                    html.Div([  
                        html.H5("Category", className='pt-4'),
                        dcc.Dropdown(
                            id="category",
                            options=[{"label": i, "value": i} for i in sorted(df["Category"].unique())],
                            value=None,
                        ),
                        html.H5("Subcategory", className='pt-4'),
                        dcc.Dropdown(
                            id="subcategory",
                            options=[{"label": i, "value": i} for i in sorted(df["Subcategory"].unique())],
                            value=None),
                        html.H5("Product", className='pt-4'),
                        dcc.Dropdown(
                            id="product",
                            options=[],
                            value=None,
                            multi=True),
                        
                        # Insert the RangeSlider for scraped_at filtering
                        html.H5("Date Range", className='pt-4'),
                        # Add the RangeSlider
                        dcc.RangeSlider(
                            id='date-range-slider',
                            min=int(df['scraped_at'].min().timestamp()),  # Convert min date to timestamp (in seconds)
                            max=int(df['scraped_at'].max().timestamp()),  # Convert max date to timestamp (in seconds)
                            value=[int(df['scraped_at'].min().timestamp()), int(df['scraped_at'].max().timestamp())],
                            # marks=date_marks,  # Only show min and max dates as labels
                            tooltip={
                                "placement": "bottom",
                                "always_visible": True,
                                "style": {"color": "LightSteelBlue", "fontSize": "20px"}
                            },
                            vertical=False  # Make the slider vertical
                        ),

                    ], className='card-body p-3'),
                ], className='card z-index-2'),
            ], className='container-fluid'),

            html.Div([
                html.Div([  
                    html.Div([ 
                        html.H4("Online Price Performance Score Over Time (Grouped by 6-hour Intervals)", className='card-header pb-0'),
                        html.Div([  
                            dcc.Graph(id="line"),
                        ], className='card-body p-3'),
                    ], className='card-body p-3'),
                ], className='card z-index-2'),
            ], className='container-fluid'),

        ], className='container-fluid'
    )
   
    # Chained Callback: Update Category dropdown based on Product and Subcategory
    @app.callback(
        Output("category", "options"),
        Input("product", "value"),
        Input("subcategory", "value")
    )
    def update_category_options(product, subcategory):
        dff = copy.deepcopy(df)
        if subcategory:
            dff = dff[dff["Subcategory"] == subcategory]
        if product:
            dff = dff[dff["Product"].isin(product)]
        return [{"label": i, "value": i} for i in sorted(dff["Category"].unique())]


    # Chained Callback: Update Subcategory dropdown based on Category and Product
    @app.callback(
        Output("subcategory", "options"),
        Input("product", "value"),
        Input("category", "value")
    )
    def update_subcategory_options(product, category):
        dff = copy.deepcopy(df)
        if category:
            dff = dff[dff["Category"] == category]
        if product:
            dff = dff[dff["Product"].isin(product)]
        return [{"label": i, "value": i} for i in sorted(dff["Subcategory"].unique())]

    # Chained Callback: Update Product dropdown based on Subcategory and Category
    @app.callback(
        Output("product", "options"),
        Input("subcategory", "value"),
        Input("category", "value")
    )
    def update_product_options(subcategory, category):
        dff = copy.deepcopy(df)
        if category:
            dff = dff[dff["Category"] == category]
        if subcategory:
            dff = dff[dff["Subcategory"] == subcategory]
        return [{"label": i, "value": i} for i in sorted(dff["Product"].unique())]


    # Line Chart Callback: Update chart based on selected Product, Subcategory, and Category
    @app.callback(
        Output("line", "figure"),
        Input("product", "value"),
        Input("subcategory", "value"),
        Input("category", "value")
    )

    def update_line_chart(product, subcategory, category):
        dff = copy.deepcopy(df)

        # Filter by category and subcategory
        if category:
            dff = dff[dff["Category"] == category]
        if subcategory:
            dff = dff[dff["Subcategory"] == subcategory]

        # Ensure 'scraped_at' is a datetime column
        dff['scraped_at'] = pd.to_datetime(dff['scraped_at'])

        # Create a 'quarter_day' column by rounding 'scraped_at' to the nearest 6 hours
        dff['quarter_day'] = dff['scraped_at'].dt.floor('6h')

        # Filter by product first
        if product:
            dff = dff[dff["Product"].isin(product)]
            # Print columns to debug
            # print("Columns after filtering by product:", dff.columns)

        # Define the price columns
        price_columns = ['amazon_price', 'nahdi_price', 'dawa_price']

        # Intersect price columns with actual columns in dff to avoid KeyError
        existing_price_columns = [col for col in price_columns if col in dff.columns]
        # print("Existing price columns:", existing_price_columns)


        # Replace 'None' and 'N/A' with NaN in existing price columns only
        dff.loc[:, existing_price_columns] = dff.loc[:, existing_price_columns].replace([None, 'N/A'], pd.NA)
        dff.loc[:, existing_price_columns] = dff.loc[:, existing_price_columns].apply(pd.to_numeric, errors='coerce')

        # Ensure only numeric columns are used in mean calculation
        numeric_cols = dff.select_dtypes(include='number').columns
        # print("numeric cols are ", numeric_cols)

        # Group by 'quarter_day' and calculate the mean of numeric columns
        grouped_df = dff.groupby('quarter_day')[numeric_cols].mean().reset_index()

        # Initialize the figure
        fig = go.Figure()

        # Loop over each product and plot their respective prices if available
        if product:
            for prod in product:
                product_data = dff[dff["Product"] == prod]
                grouped_product_df = product_data.groupby('quarter_day')[numeric_cols].mean().reset_index()

                # Check and add traces for existing price columns only
                for col in existing_price_columns:
                    if col in grouped_product_df.columns:
                        fig.add_trace(go.Scatter(
                            x=grouped_product_df['quarter_day'],
                            y=grouped_product_df[col],
                            mode='lines',
                            name=f'{col.replace("_price", "").capitalize()} Price for {prod}'
                        ))

        # Plot the average prices for all selected products, only for existing columns
        for col in existing_price_columns:
            if col in grouped_df.columns:
                fig.add_trace(go.Scatter(
                    x=grouped_df['quarter_day'],
                    y=grouped_df[col],
                    mode='lines',
                    name=f'Average {col.replace("_price", "").capitalize()} Price',
                    line=dict(dash='dash')
                ))

        return fig

        # Plot for each selected product
        # if product:
        #     for prod in product:
        #         product_data = dff[dff["Product"] == prod]
        #         grouped_product_df = product_data.groupby('quarter_day')[numeric_cols].mean().reset_index()

        #         fig.add_trace(go.Scatter(
        #             x=grouped_product_df['quarter_day'],
        #             y=grouped_product_df['opps'],  # Assuming 'opps' is a numeric field
        #             mode='lines',
        #             name=f'OPPS for {prod}'
        #         ))

        # # Plot the average OPPS for all selected products
        # fig.add_trace(go.Scatter(
        #     x=grouped_df['quarter_day'],
        #     y=grouped_df['opps'],
        #     mode='lines',
        #     name='Average OPPS',
        #     line=dict(dash='dash')
        # ))

        # # Update the layout of the figure
        # fig.update_layout(
        #     xaxis_title="Scraped Date (Quarter Day)",
        #     yaxis_title="OPPS",
        #     template="plotly_white"
        # )

        # return fig



    return app


# def plot_dashboard(data):
#     df = pd.DataFrame(data)
#     df['Category'] = df['Category'].astype(str)
#     df['Subcategory'] = df['Subcategory'].astype(str)
#     df['Product'] = df['Product'].astype(str)

#     app = DjangoDash('OPPS_Line', external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])


#     app.layout = html.Div(
#         [ html.Div( [ 
#     html.Div( [  
#         html.Div( [  
#             html.Div( [ 
#                         html.H5("Category",
#                             className='pt-4',),
#                         dcc.Dropdown(
#                             id="category",
#                             options=[{"label": i, "value": i} for i in sorted(df["Category"].unique())],
#                             value=None,
#                         ),
#                         html.H5("Subcategory",
#                             className='pt-4'),
#                         dcc.Dropdown(
#                             id="subcategory",
#                             options=[{"label": i, "value": i} for i in sorted(df["Subcategory"].unique())],
#                             value=None),
#                         html.H5("Product",
#                             className='pt-4'),
#                         dcc.Dropdown(
#                             id="product",
#                             options=[],
#                             value=None,
#                             multi=True),
#             ],className='card-body p-3' ),
#         ],className='card z-index-2' ),
#     ],className='col-lg-4')
#     ,
#     html.Div( [ 
#         html.Div( [  
#                 html.Div( [ 
#                     html.Div( [  
#                         html.H4("Online Precie Performance Score Over Time (Grouped by 6-hour Intervals)"),
#                     ],className='card-header pb-0' ),
#                     html.Div( [  
#                         dcc.Graph(id="line"),
#                     ],className='card-body p-3' ),
#             ],className='card-body p-3' ),
#         ],className='card z-index-2' ),
#     ],className='col-lg-8'),
#     ],className='row mt-4')
#     ],className='container-fluid')
   


#     # Chained Callback: Update Subcategory dropdown based on Category and Product
#     @app.callback(
#         Output("subcategory", "options"),
#         Input("product", "value"),
#         Input("category", "value")
#     )
#     def update_subcategory_options(product, category):
#         dff = copy.deepcopy(df)
#         if category:
#             dff = dff[dff["Category"] == category]
#         if product:
#             dff = dff[dff["Product"].isin(product)]
#         return [{"label": i, "value": i} for i in sorted(dff["Subcategory"].unique())]

#     # Chained Callback: Update Product dropdown based on Subcategory and Category
#     @app.callback(
#         Output("product", "options"),
#         Input("subcategory", "value"),
#         Input("category", "value")
#     )
#     def update_product_options(subcategory, category):
#         dff = copy.deepcopy(df)
#         if category:
#             dff = dff[dff["Category"] == category]
#         if subcategory:
#             dff = dff[dff["Subcategory"] == subcategory]
#         return [{"label": i, "value": i} for i in sorted(dff["Product"].unique())]

#     # Chained Callback: Update Category dropdown based on Product and Subcategory
#     @app.callback(
#         Output("category", "options"),
#         Input("product", "value"),
#         Input("subcategory", "value")
#     )
#     def update_category_options(product, subcategory):
#         dff = copy.deepcopy(df)
#         if subcategory:
#             dff = dff[dff["Subcategory"] == subcategory]
#         if product:
#             dff = dff[dff["Product"].isin(product)]
#         return [{"label": i, "value": i} for i in sorted(dff["Category"].unique())]

#     @app.callback(
#         Output("line", "figure"),
#         Input("product", "value"),
#         Input("subcategory", "value"),
#         Input("category", "value")
#     )
#     def update_line_chart(product, subcategory, category):
#         dff = copy.deepcopy(df)

#         # Filter by category and subcategory
#         if category:
#             dff = dff[dff["Category"] == category]
#         if subcategory:
#             dff = dff[dff["Subcategory"] == subcategory]

#         # Ensure 'scraped_at' is a datetime column
#         dff['scraped_at'] = pd.to_datetime(dff['scraped_at'])

#         # Create a 'quarter_day' column by rounding 'scraped_at' to the nearest 6 hours
#         dff['quarter_day'] = dff['scraped_at'].dt.floor('6h')

#         # Filter for multiple products
#         if product:
#             dff = dff[dff["Product"].isin(product)]

#         # Ensure only numeric columns are used in mean calculation
#         numeric_cols = dff.select_dtypes(include='number').columns

#         # Group by 'quarter_day' and calculate the mean of numeric columns
#         grouped_df = dff.groupby('quarter_day')[numeric_cols].mean().reset_index()

#         # Plot the data using plotly.graph_objs
#         fig = go.Figure()

#         # Plot for each selected product's prices
#         if product:
#             for prod in product:
#                 product_data = dff[dff["Product"] == prod]
#                 grouped_product_df = product_data.groupby('quarter_day')[numeric_cols].mean().reset_index()

#                 # Check if the necessary price columns exist before plotting
#                 if 'amazon_price' in grouped_product_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_product_df['quarter_day'],
#                         y=grouped_product_df['amazon_price'],  # Change to desired price field
#                         mode='lines',
#                         name=f'Amazon Price for {prod}'
#                     ))

#                 if 'nahdi_price' in grouped_product_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_product_df['quarter_day'],
#                         y=grouped_product_df['nahdi_price'],  # Change to desired price field
#                         mode='lines',
#                         name=f'Nahdi Price for {prod}'
#                     ))

#                 if 'dawa_price' in grouped_product_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_product_df['quarter_day'],
#                         y=grouped_product_df['dawa_price'],  # Change to desired price field
#                         mode='lines',
#                         name=f'Dawa Price for {prod}'
#                     ))

#         # Plot the average prices for all selected products
#         if 'amazon_price' in grouped_df.columns:
#             fig.add_trace(go.Scatter(
#                 x=grouped_df['quarter_day'],
#                 y=grouped_df['amazon_price'],
#                 mode='lines',
#                 name='Average Amazon Price',
#                 line=dict(dash='dash')
#             ))

#         if 'nahdi_price' in grouped_df.columns:
#             fig.add_trace(go.Scatter(
#                 x=grouped_df['quarter_day'],
#                 y=grouped_df['nahdi_price'],
#                 mode='lines',
#                 name='Average Nahdi Price',
#                 line=dict(dash='dash')
#             ))

#         if 'dawa_price' in grouped_df.columns:
#             fig.add_trace(go.Scatter(
#                 x=grouped_df['quarter_day'],
#                 y=grouped_df['dawa_price'],
#                 mode='lines',
#                 name='Average Dawa Price',
#                 line=dict(dash='dash')
#             ))

#         # Update the layout of the figure
#         fig.update_layout(
#             xaxis_title="Scraped Date (Quarter Day)",
#             yaxis_title="Prices",
#             template="plotly_white"
#         )

#         return fig

#     return app

