
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
from dash import dcc, html, Input, Output, callback
from django_plotly_dash import DjangoDash
import copy
import json
from plotly.subplots import make_subplots
import zlib
from dashboard.utils import get_materialized_view_data  # Adjust import path as needed



def plot_dashboard(df, user_accounts):
    # df = get_materialized_view_data(period)


    app = DjangoDash('OPPS_Line', external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])
    app.layout = html.Div(
        [
            html.Div([
                html.Div([
                    html.H5("Product", className='pt-4'),
                    dcc.Dropdown(
                        id="product",
                        options=[{"label": i, "value": i} for i in sorted(df["product_name"].unique())],
                        # options=[{"label": i, "value": i} for i in sorted(filter(lambda x: x is not None, df[df['Competitor'] == 'False']["Product"].unique()))],
                        value=None,
                        multi=False
                    ),
                    html.H5("Period", className='pt-4'),
                    dcc.Dropdown(
                        id="period",
                        options=[
                            {"label": "Last Week", "value": "last_week"},
                            {"label": "Last Month", "value": "last_month"},
                            {"label": "Last 6 Months", "value": "last_6_months"},
                            {"label": "Last Year", "value": "last_year"},
                            {"label": "Year to Date", "value": "ytd"}
                        ],
                        value="last_week",
                        multi=False
                    ),
                    html.H5("Account", className='pt-4'),
                    dcc.Dropdown(
                        id="account",
                        options=[{"label": account, "value": account} for account in user_accounts],
                        value=None,
                        multi=True
                    ),
                    html.H5("Plot Type", className='pt-4'),
                    dcc.Dropdown(
                        id="plot-types",
                        options=[
                            {"label": "Account Prices", "value": "account_prices"},
                            {"label": "Promo Depth", "value": "promo_depth"},
                            {"label": "Market Sahre", "value": "market_share"},
                        ],
                        value=None,
                        multi=False
                    ),
                    # Advanced Overlay Dropdown
                    html.H5("Advanced Overlay", className='pt-4', id='overlay-header'),
                    dcc.Dropdown(
                        id="advanced-overlay",
                        options=[
                            {"label": "Category", "value": "category"},
                            {"label": "Subcategory", "value": "subcategory"},
                            {"label": "Competitor", "value": "competitor"},
                            {"label": "Online Price Performance Score", "value": "OPPS"},
                        ],
                        value=None,
                        multi=True
                    ),
                ], className='card-body p-3'),
            ], className='container-fluid'),

            html.Div([
                html.Div([
                    # html.H4("Online Price Performance Score Over Time (Grouped by 6-hour Intervals)", className='card-header pb-0'),
                    html.Div([
                        dcc.Graph(id="line"),
                    ]),
                ], className='card-body p-3'),
                    html.Div([
                        dcc.Graph(id="competitor-graph", style={"display": "none"}),  # Secondary graph
                    ], className='card-body p-3'),
            ], className='container-fluid'),
        ], className='container-fluid'
    )

    # Callback to toggle the visibility of the advanced overlay dropdown
    @app.callback(
        Output('advanced-overlay', 'style'),
        Output('overlay-header', 'style'),
        Input('plot-types', 'value')
    )
    def toggle_advanced_overlay(plot_types):
        if plot_types in ["account_prices", "market_share", "promo_depth"]:
            return {'display': 'block'}, {'display': 'block'}  # Show overlay dropdown and header
        return {'display': 'none'}, {'display': 'none'}  # Hide overlay dropdown and header

   

    @app.callback(
    [
        Output("line", "figure"),  # Primary graph
        Output("competitor-graph", "figure"),  # Secondary graph
        Output("competitor-graph", "style"),  # Secondary graph visibility
    ],
    [
        Input("product", "value"),
        Input("period", "value"),
        Input("account", "value"),
        Input("plot-types", "value"),
        Input("advanced-overlay", "value")  # Advanced overlay input
    ]
)



    def update_line_chart(product, period, selected_accounts, plot_types, advanced_overlay):
        df = get_materialized_view_data(period)
        
        # Rest of your existing processing logic
        period_df = df.copy()  # No need to filter by period since the view already does this
        


        # Filter the combined DataFrame for the selected period
        period_df = df[df['period'] == period].copy()

        # Ensure scraped_at is in datetime format
        period_df.loc[:, 'agregated_time'] = pd.to_datetime(period_df['scraped_at'], errors='coerce').dt.tz_localize(None)

        # Check for any NaT values after conversion
        if period_df['agregated_time'].isnull().any():
            raise ValueError("There are invalid dates in the scraped_at column.")

        # Ensure numeric columns are cleaned and converted
        numeric_columns = [
            'amazon_price', 'nahdi_price', 'dawa_price', 'noon_sa_price',
            'amazon_discount', 'dawa_discount', 'noon_sa_discount', 'nahdi_discount',
            'nahdi_ordered_qty'
        ]

        for col in numeric_columns:
            if col in period_df.columns:
                period_df.loc[:, col] = pd.to_numeric(period_df[col].replace([None, 'N/A'], pd.NA), errors='coerce')

        if product:
            # Filter for the selected product
            dff = period_df[period_df["Product"] == product]

            dff.loc[:, numeric_columns] = dff[numeric_columns].replace([None, 'N/A'], pd.NA).apply(pd.to_numeric, errors='coerce')

            # Fetch the competitor references for the selected product
            from client_profile.models import Product
            try:
                product_instance = Product.objects.get(TITLE=product)
                competitor_references = product_instance.competitor_references.all()
                competitor_reference_titles = [ref.TITLE for ref in competitor_references]
            except Product.DoesNotExist:
                competitor_reference_titles = []

            # Filter for category or subcategory match with key_name
            categories = list(dff['Category'].dropna().unique())
            subcategories = list(dff['Subcategory'].dropna().unique())

            # Create competitor_df based on the filtered categories and subcategories for Competitor == True
            competitor_df = period_df[
                # (period_df['Competitor'] == 'True') & 
                # (period_df['Category'].isin(categories) | period_df['Subcategory'].isin(subcategories))
                (period_df['Product'].isin(competitor_reference_titles))  
            ]
            competitor_df = competitor_df.sort_values(by=['Product', 'scraped_at'], ascending=[True, False])

            # Filter bulk_df where key_name matches any Category or Subcategory in dff
            bulk_df = period_df[period_df["key_name"].isin(categories + subcategories)]
            bulk_df = bulk_df.sort_values(by=['nahdi_title', 'agregated_time'], ascending=[True, False])

            # Prepare category_df and subcategory_df
            category_df = bulk_df[bulk_df['key_name'].isin(categories)]
            subcategory_df = bulk_df[bulk_df['key_name'].isin(subcategories)]

            # Sort dff by Product and scraped_at
            grouped_df = dff.sort_values(by=['Product', 'agregated_time'], ascending=[True, False])

            # Debug: Save intermediate DataFrames to CSV for inspection
            # grouped_df.to_csv('dff.csv')
            # category_df.to_csv('category_df.csv')
            # subcategory_df.to_csv('subcategory_df.csv')
            # competitor_df.to_csv('competitor_df.csv')


        
        fig = go.Figure()
        competitor_fig = go.Figure()
        competitor_style = {"display": "none"}  # Hide secondary graph by default

        

        # Acount Price 
        if plot_types == 'account_prices':
            # Iterate over each account in selected_accounts
            for account in selected_accounts:
                account_price_column = f"{account}_price"
                # Check if the account price column exists in grouped_df before plotting
                if account_price_column in grouped_df.columns:
                    fig.add_trace(go.Scatter(
                        x=grouped_df['agregated_time'],
                        y=grouped_df[account_price_column],
                        mode='lines',
                        name=f"{account.capitalize()} Price"
                    ))

            if 'RSP_VAT' in grouped_df.columns:
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df['RSP_VAT'],
                    mode='lines',
                    name="RSP VAT",
                    line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot')
                ))

            # Calculate the average across the selected account columns
            account_columns = []
            if 'amazon' in selected_accounts and 'amazon_price' in grouped_df.columns:
                account_columns.append('amazon_price')
            if 'nahdi' in selected_accounts and 'nahdi_price' in grouped_df.columns:
                account_columns.append('nahdi_price')
            if 'dawa' in selected_accounts and 'dawa_price' in grouped_df.columns:
                account_columns.append('dawa_price')
            if 'noon_sa' in selected_accounts and 'noon_sa_price' in grouped_df.columns:
                account_columns.append('noon_sa_price')

            if account_columns:
                grouped_df["average_price"] = grouped_df[account_columns].mean(axis=1)
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df["average_price"],
                    mode='lines',
                    name="Average Price",
                    line=dict(width=4, color='blue', dash='solid')
                ))

            # Check if advanced overlay is set to "category"
            if advanced_overlay and 'category' in advanced_overlay:
                for account in selected_accounts:
                    account_price_column = f"{account}_price"
                    
                    # Ensure category_df is available and not empty
                    if not category_df.empty:
                        # Add scatter plot for the category_df data
                        fig.add_trace(go.Scatter(
                            x=category_df['agregated_time'],
                            y=category_df[account_price_column],
                            mode='markers',
                            name=f"{account} - Category ({categories})",
                            marker=dict(size=8, symbol='circle'),
                            text=category_df[f"{account}_title"],  # Add the account_title to display on hover
                            hoverinfo='text',  # Show the 'text' value on hover
                        ))
                    else:
                        print(f"No data found for subcategory overlay.")

            # Check if advanced overlay is set to "subcategory"
            if advanced_overlay and 'subcategory' in advanced_overlay:

                for account in selected_accounts:
                    account_price_column = f"{account}_price"
                    
                    # Ensure category_df is available and not empty
                    if not subcategory_df.empty:
                        # Add scatter plot for the category_df data
                        fig.add_trace(go.Scatter(
                            x=subcategory_df['agregated_time'],
                            y=subcategory_df[account_price_column],
                            mode='markers',
                            name=f"{account} - Subcategory ({subcategories})",
                            marker=dict(size=8, symbol='circle'),
                            text=subcategory_df[f"{account}_title"],  # Add the account_title to display on hover
                            hoverinfo='text',  # Show the 'text' value on hover
                        ))
                    else:
                        print(f"No data found for category overlay.")

            # Check if advanced overlay is set to "OPPS"
            if advanced_overlay and 'OPPS' in advanced_overlay:
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df['opps'],
                    mode='lines',
                    name="Online Price Performance Score",
                    line=dict(width=4, color='red', dash='solid'),
                    yaxis="y2"  # Assigning this trace to the secondary y-axis
                ))

            # Check if advanced overlay is set to "competitor"
            if advanced_overlay and 'competitor' in advanced_overlay:
                for account in selected_accounts:
                    account_price_column = f"{account}_price"

                    # Add 'Product' as a column instead of an index
                    competitor_df_grouped = competitor_df.groupby('Product').agg(
                        avg_price=(account_price_column, 'mean'),
                    )
                    competitor_df_grouped = competitor_df_grouped.sort_values(by='avg_price', ascending=False)
                    competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column


                    # Calculate dynamic height for the chart
                    chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
                    # Create secondary figure for competitor analysis
                    competitor_fig.add_trace(go.Bar(
                        y=[label[:20] + "..." if len(label) > 20 else label for label in competitor_df_grouped['Product']],
                        x=competitor_df_grouped['avg_price'],
                        orientation='h',
                        name= f'Average Price per Competitors for {account}',
                        # marker=dict(color='rgba(255, 99, 71, 0.6)'),
                        hovertext=competitor_df_grouped['Product'],  # Full product name for hover
                        hoverinfo="text+x"  # Display both the hovertext and x-value

                    ))

                    competitor_fig.update_layout(
                        title={
                        'text': "Average Price Per Competitors",
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },

                        xaxis_title="Price SAR",
                        yaxis_title="Products",
                        template="plotly_white",
                        height=chart_height
                    )

                    # Make the secondary graph visible
                    competitor_style = {"display": "block"}

            # Update layout to include secondary y-axis
            fig.update_layout(
                xaxis_title="Days",
                yaxis_title="Product Price SAR",  # Primary y-axis title
                yaxis2=dict(
                    title="Online Price Performance Score",  # Secondary y-axis title
                    overlaying="y",  # Overlay this axis on top of the primary y-axis
                    side="right",  # Position the secondary y-axis on the right
                    showgrid=False  # Optionally hide grid lines for the secondary axis
                ),
                title={
                    'text': "Product Price Over Time",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

        # Promo Depth
        if plot_types == 'promo_depth':
            # Iterate over each account in selected_accounts
            for account in selected_accounts:
                account_discount_column = f"{account}_discount"
                # Check if the account discount column exists in grouped_df before plotting
                if account_discount_column in grouped_df.columns:
                    fig.add_trace(go.Scatter(
                        x=grouped_df['agregated_time'],
                        y=grouped_df[account_discount_column],
                        mode='lines',
                        name=f"{account.capitalize()} Discount"
                    ))

            if 'discount_percentage' in grouped_df.columns:
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df['discount_percentage'],
                    mode='lines',
                    name="Promo discount",
                    line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot')
                ))

            # Calculate the average across the selected account columns
            account_columns = []
            if 'amazon' in selected_accounts and 'amazon_discount' in grouped_df.columns:
                account_columns.append('amazon_discount')
            if 'nahdi' in selected_accounts and 'nahdi_discount' in grouped_df.columns:
                account_columns.append('nahdi_discount')
            if 'dawa' in selected_accounts and 'dawa_discount' in grouped_df.columns:
                account_columns.append('dawa_discount')
            if 'noon_sa' in selected_accounts and 'noon_sa_discount' in grouped_df.columns:
                account_columns.append('noon_sa_discount')

            if account_columns:
                grouped_df["average_discounts"] = grouped_df[account_columns].mean(axis=1)
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df["average_discounts"],
                    mode='lines',
                    name="Average Promo Discounts",
                    line=dict(width=4, color='blue', dash='solid')
                ))

            # Check if advanced overlay is set to "category"
            if advanced_overlay and 'category' in advanced_overlay:
                for account in selected_accounts:
                    account_discount_column = f"{account}_discount"
                    # Ensure category_df is available and not empty
                    if not category_df.empty:
                        # Add scatter plot for the category_df data
                        fig.add_trace(go.Scatter(
                            x=category_df['agregated_time'],
                            y=category_df[account_discount_column],
                            mode='markers',
                            name=f"{account} - Category ({categories})",
                            marker=dict(size=8, symbol='circle'),
                            text=category_df[f"{account}_title"],  # Add the account_title to display on hover
                            hoverinfo='text',  # Show the 'text' value on hover
                        ))
                    else:
                        print(f"No data found for subcategory overlay.")

            # Check if advanced overlay is set to "subcategory"
            if advanced_overlay and 'subcategory' in advanced_overlay:
                for account in selected_accounts:
                    account_discount_column = f"{account}_discount"
                    # Ensure category_df is available and not empty
                    if not subcategory_df.empty:
                        # Add scatter plot for the category_df data
                        fig.add_trace(go.Scatter(
                            x=subcategory_df['agregated_time'],
                            y=subcategory_df[account_discount_column],
                            mode='markers',
                            name=f"{account} - Subcategory ({subcategories})",
                            marker=dict(size=8, symbol='circle'),
                            text=subcategory_df[f"{account}_title"],  # Add the account_title to display on hover
                            hoverinfo='text',  # Show the 'text' value on hover
                        ))
                    else:
                        print(f"No data found for Subcategory overlay.")

            # Check if advanced overlay is set to "OPPS"
            if advanced_overlay and 'OPPS' in advanced_overlay:
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df['opps'],
                    mode='lines',
                    name="Online Price Performance Score",
                    line=dict(width=4, color='red', dash='solid'),
                    yaxis="y2"  # Assigning this trace to the secondary y-axis
                ))

            # Check if advanced overlay is set to "competitor"
            if advanced_overlay and 'competitor' in advanced_overlay:
                for account in selected_accounts:
                    account_discount_column = f"{account}_discount"

                    # Add 'Product' as a column instead of an index
                    competitor_df_grouped = competitor_df.groupby('Product').agg(
                        avg_promo=(account_discount_column, 'mean'),
                    )
                    competitor_df_grouped = competitor_df_grouped.sort_values(by='avg_promo', ascending=False)
                    competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column


                    # Calculate dynamic height for the chart
                    chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
                    # Create secondary figure for competitor analysis
                    competitor_fig.add_trace(go.Bar(
                        y=[label[:20] + "..." if len(label) > 20 else label for label in competitor_df_grouped['Product']],
                        x=competitor_df_grouped['avg_promo'],
                        orientation='h',
                        name= f'Average Promo per Competitors for {account}',
                        # marker=dict(color='rgba(255, 99, 71, 0.6)'),
                        hovertext=competitor_df_grouped['Product'],  # Full product name for hover
                        hoverinfo="text+x"  # Display both the hovertext and x-value

                    ))

                    competitor_fig.update_layout(
                        title={
                        'text': "Average Promo Per Competitors",
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },

                        xaxis_title="Discount Percent",
                        yaxis_title="Products",
                        template="plotly_white",
                        height=chart_height
                    )

                    # Make the secondary graph visible
                    competitor_style = {"display": "block"}


            # Update layout to include secondary y-axis
            fig.update_layout(
                xaxis_title="Days",
                yaxis_title="Discount Percent",  # Primary y-axis title
                yaxis2=dict(
                    title="Online Price Performance Score",  # Secondary y-axis title
                    overlaying="y",  # Overlay this axis on top of the primary y-axis
                    side="right",  # Position the secondary y-axis on the right
                    showgrid=False  # Optionally hide grid lines for the secondary axis
                ),
                title={
                    'text': "Promo Discount Over Time",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

        # Market Share 
        if plot_types == 'market_share':

            # Step 1: Shift 'nahdi_ordered_qty' by 1 within each product group
            grouped_df['order_bfr'] = grouped_df['nahdi_ordered_qty'].shift(-1)

            # Step 2: Calculate 'ordered_qty' as the difference between current and previous order quantity
            grouped_df['ordered_qty'] = grouped_df['nahdi_ordered_qty'] -  grouped_df['order_bfr'] 
            # grouped_df.to_csv('dff_calc.csv')
            fig.add_trace(go.Bar(
            x=grouped_df['agregated_time'],
            y=grouped_df['ordered_qty'],
            name='Total Order Quantity'
        ))

            # Add OPPS line if selected
            if advanced_overlay and 'OPPS' in advanced_overlay :
                fig.add_trace(go.Scatter(
                    x=grouped_df['agregated_time'],
                    y=grouped_df['opps'],
                    mode='lines',
                    name="Online Price Performance Score",
                    line=dict(width=4, color='red', dash='solid'),
                    yaxis="y2"  # Assigning this trace to the secondary y-axis
                ))

            fig.update_layout(
                xaxis_title="Days",
                yaxis_title="Unit Solds",  # Primary y-axis title
                yaxis2=dict(
                    title="Online Price Performance Score",  # Secondary y-axis title
                    overlaying="y",  # Overlay this axis on top of the primary y-axis
                    side="right",  # Position the secondary y-axis on the right
                    showgrid=False  # Optionally hide grid lines for the secondary axis
                ),
                title={
                    'text': "Market Share Analysis: Order Quantity Per Selected Period",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                template="plotly_white",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1

                )
            )

            
            if advanced_overlay and 'competitor' in advanced_overlay:
                # Add 'Product' as a column instead of an index
                competitor_df_grouped = competitor_df.groupby('Product').agg(
                    max_ordered_qty=('nahdi_ordered_qty', 'max'),
                    min_ordered_qty=('nahdi_ordered_qty', 'min')
                )
                competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
                competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
                competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column

                # Similarly for product_grouped
                product_grouped = dff.groupby('Product').agg(
                    max_ordered_qty=('nahdi_ordered_qty', 'max'),
                    min_ordered_qty=('nahdi_ordered_qty', 'min')
                )
                product_grouped['unit_sold'] = product_grouped['max_ordered_qty'] - product_grouped['min_ordered_qty']
                product_grouped = product_grouped.reset_index()  # Reset index to make 'Product' a column

                # Concatenate the two DataFrames
                combined_df = pd.concat([product_grouped, competitor_df_grouped], ignore_index=True)
                # combined_df.to_csv('combined_df.csv')
                # dff.to_csv('dff.csv')
                # product_grouped.to_csv('product_grouped.csv')
                # Calculate dynamic height for the chart
                chart_height = max(400, len(combined_df) * 30)  # Minimum 400px, 30px per bar
                # Create secondary figure for competitor analysis
                competitor_fig.add_trace(go.Bar(
                    y=[label[:20] + "..." if len(label) > 20 else label for label in combined_df['Product']],
                    x=combined_df['unit_sold'],
                    orientation='h',
                    name='Unit Sold per Competitor',
                    marker=dict(color='rgba(255, 99, 71, 0.6)'),
                    hovertext=combined_df['Product'],  # Full product name for hover
                    hoverinfo="text+x"  # Display both the hovertext and x-value

                ))

                competitor_fig.update_layout(
                    title={
                    'text': "Market Share Analysis",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },

                    xaxis_title="Unit Sold",
                    yaxis_title="Products",
                    template="plotly_white",
                    height=chart_height
                )

                # Make the secondary graph visible
                competitor_style = {"display": "block"}


            if advanced_overlay and 'category' in advanced_overlay:
                # Add 'Product' as a column instead of an index
                competitor_df_grouped = category_df.groupby('nahdi_title').agg(
                    max_ordered_qty=('nahdi_ordered_qty', 'max'),
                    min_ordered_qty=('nahdi_ordered_qty', 'min')
                )
                competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
                competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
                competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column
                # Calculate dynamic height for the chart
                chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
                
                # Create unique y labels to handle duplicate initial characters
                competitor_df_grouped['unique_label'] = [
                    f"{label[:20]}... ({i})" if len(label) > 20 else f"{label} ({i})"
                    for i, label in enumerate(competitor_df_grouped['nahdi_title'], start=1)
                ]


                # Create secondary figure for competitor analysis
                competitor_fig.add_trace(go.Bar(
                    y=competitor_df_grouped['unique_label'],  # Use unique y labels
                    x=competitor_df_grouped['unit_sold'],
                    orientation='h',
                    name=f'Unit Sold per Category {categories}',
                    marker=dict(
                        color='rgba(75, 192, 192, 0.6)',  # Alternate color
                    ),
                    hovertext=competitor_df_grouped['nahdi_title'],  # Full product name for hover
                    hoverinfo="text+x"  # Display both the hovertext and x-value

                ))

                competitor_fig.update_layout(
                    title={
                        'text': "Market Share Analysis",
                        'y': 0.9,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    },
                    xaxis_title="Unit Sold",
                    yaxis_title="Products",
                    yaxis=dict(
                        showticklabels=False,  # Hide y-axis tick labels
                        showgrid=False  # Hide grid lines for y-axis
                    ),
                    template="plotly_white",
                    height=chart_height,  # Set dynamic height
                )

                # Make the secondary graph visible
                competitor_style = {"display": "block"}


            if advanced_overlay and 'subcategory' in advanced_overlay:
                # Add 'Product' as a column instead of an index
                competitor_df_grouped = subcategory_df.groupby('nahdi_title').agg(
                    max_ordered_qty=('nahdi_ordered_qty', 'max'),
                    min_ordered_qty=('nahdi_ordered_qty', 'min')
                )
                competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
                competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
                competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column

                # Calculate dynamic height for the chart
                chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
                                # Create unique y labels to handle duplicate initial characters
                competitor_df_grouped['unique_label'] = [
                    f"{label[:20]}... ({i})" if len(label) > 20 else f"{label} ({i})"
                    for i, label in enumerate(competitor_df_grouped['nahdi_title'], start=1)
                ]

                # Create secondary figure for competitor analysis
                competitor_fig.add_trace(go.Bar(
                    y=competitor_df_grouped['unique_label'],  # Use unique y labels
                    x=competitor_df_grouped['unit_sold'],
                    orientation='h',
                    name=f'Unit Sold per Subcategory {subcategories}',
                    marker=dict(color='rgba(153, 102, 255, 0.6)'),
                    hovertext=competitor_df_grouped['nahdi_title'],  # Full product name for hover
                    hoverinfo="text+x"  # Display both the hovertext and x-value

                ))

                competitor_fig.update_layout(
                    title={
                    'text': "Market Share Analysis",
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },

                    xaxis_title="Unit Sold",
                    yaxis_title="Products",
                    yaxis=dict(
                        showticklabels=False,  # Hide y-axis tick labels
                        showgrid=False  # Hide grid lines for y-axis
                    ),                    template="plotly_white",
                    height=chart_height
                )

                # Make the secondary graph visible
                competitor_style = {"display": "block"}


        return fig, competitor_fig, competitor_style

    return app


# # Old function changed on 24/Mar
# def plot_dashboard(compressed_data, user_accounts):
#     # Decompress the cached data
#     try:
#         decompressed_data = zlib.decompress(compressed_data).decode('utf-8')
#         precomputed_data = json.loads(decompressed_data)
#     except Exception as e:
#         raise ValueError(f"Failed to decompress or deserialize cached data: {e}")

#     # Debug: Print precomputed_data keys
#     # print("Precomputed data keys:", precomputed_data.keys())

#     # Convert precomputed_data back into DataFrames
#     for key in precomputed_data:
#         precomputed_data[key] = pd.DataFrame(precomputed_data[key])

#     # Debug: Print column names and first few rows of each DataFrame
#     # for key in precomputed_data:
#     #     print(f"Columns in {key}: {precomputed_data[key].columns}")
#     #     print(f"First few rows of {key}:\n{precomputed_data[key].head()}")


#     # Append all periods into one DataFrame with a 'period' key
#     df = pd.concat(
#         {key: df for key, df in precomputed_data.items()},
#         names=['period']
#     ).reset_index(level=0).rename(columns={'level_0': 'period'})

#     # Debug: Print combined DataFrame
#     # df.to_csv('df_main_investigations.csv')


#     app = DjangoDash('OPPS_Line', external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])
#     app.layout = html.Div(
#         [
#             html.Div([
#                 html.Div([
#                     html.H5("Product", className='pt-4'),
#                     dcc.Dropdown(
#                         id="product",
#                         # options=[{"label": i, "value": i} for i in sorted(df["Product"].unique())],
#                         options=[{"label": i, "value": i} for i in sorted(filter(lambda x: x is not None, df[df['Competitor'] == 'False']["Product"].unique()))],
#                         value=None,
#                         multi=False
#                     ),
#                     html.H5("Period", className='pt-4'),
#                     dcc.Dropdown(
#                         id="period",
#                         options=[
#                             {"label": "Last Week", "value": "last_week"},
#                             {"label": "Last Month", "value": "last_month"},
#                             {"label": "Last 6 Months", "value": "last_6_months"},
#                             {"label": "Last Year", "value": "last_year"},
#                             {"label": "Year to Date", "value": "ytd"}
#                         ],
#                         value="last_week",
#                         multi=False
#                     ),
#                     html.H5("Account", className='pt-4'),
#                     dcc.Dropdown(
#                         id="account",
#                         options=[{"label": account, "value": account} for account in user_accounts],
#                         value=None,
#                         multi=True
#                     ),
#                     html.H5("Plot Type", className='pt-4'),
#                     dcc.Dropdown(
#                         id="plot-types",
#                         options=[
#                             {"label": "Account Prices", "value": "account_prices"},
#                             {"label": "Promo Depth", "value": "promo_depth"},
#                             {"label": "Market Sahre", "value": "market_share"},
#                         ],
#                         value=None,
#                         multi=False
#                     ),
#                     # Advanced Overlay Dropdown
#                     html.H5("Advanced Overlay", className='pt-4', id='overlay-header'),
#                     dcc.Dropdown(
#                         id="advanced-overlay",
#                         options=[
#                             {"label": "Category", "value": "category"},
#                             {"label": "Subcategory", "value": "subcategory"},
#                             {"label": "Competitor", "value": "competitor"},
#                             {"label": "Online Price Performance Score", "value": "OPPS"},
#                         ],
#                         value=None,
#                         multi=True
#                     ),
#                 ], className='card-body p-3'),
#             ], className='container-fluid'),

#             html.Div([
#                 html.Div([
#                     # html.H4("Online Price Performance Score Over Time (Grouped by 6-hour Intervals)", className='card-header pb-0'),
#                     html.Div([
#                         dcc.Graph(id="line"),
#                     ]),
#                 ], className='card-body p-3'),
#                     html.Div([
#                         dcc.Graph(id="competitor-graph", style={"display": "none"}),  # Secondary graph
#                     ], className='card-body p-3'),
#             ], className='container-fluid'),
#         ], className='container-fluid'
#     )

#     # Callback to toggle the visibility of the advanced overlay dropdown
#     @app.callback(
#         Output('advanced-overlay', 'style'),
#         Output('overlay-header', 'style'),
#         Input('plot-types', 'value')
#     )
#     def toggle_advanced_overlay(plot_types):
#         if plot_types in ["account_prices", "market_share", "promo_depth"]:
#             return {'display': 'block'}, {'display': 'block'}  # Show overlay dropdown and header
#         return {'display': 'none'}, {'display': 'none'}  # Hide overlay dropdown and header

   

#     @app.callback(
#     [
#         Output("line", "figure"),  # Primary graph
#         Output("competitor-graph", "figure"),  # Secondary graph
#         Output("competitor-graph", "style"),  # Secondary graph visibility
#     ],
#     [
#         Input("product", "value"),
#         Input("period", "value"),
#         Input("account", "value"),
#         Input("plot-types", "value"),
#         Input("advanced-overlay", "value")  # Advanced overlay input
#     ]
# )



#     def update_line_chart(product, period, selected_accounts, plot_types, advanced_overlay):
#         # Initial debug statement to confirm callback input values
#         # print(f"Product: {product}, Period: {period}, Accounts: {selected_accounts}, Plot Type: {plot_types}, Overlay: {advanced_overlay}")

#         if selected_accounts is None:
#             selected_accounts = []

#         # Check if the selected period exists in precomputed_data
#         if period not in precomputed_data:
#             raise ValueError(f"Invalid period: {period}. Please choose a valid period.")

#         # Filter the combined DataFrame for the selected period
#         period_df = df[df['period'] == period].copy()

#         # Ensure scraped_at is in datetime format
#         period_df.loc[:, 'agregated_time'] = pd.to_datetime(period_df['scraped_at'], errors='coerce').dt.tz_localize(None)

#         # Check for any NaT values after conversion
#         if period_df['agregated_time'].isnull().any():
#             raise ValueError("There are invalid dates in the scraped_at column.")

#         # Ensure numeric columns are cleaned and converted
#         numeric_columns = [
#             'amazon_price', 'nahdi_price', 'dawa_price', 'noon_sa_price',
#             'amazon_discount', 'dawa_discount', 'noon_sa_discount', 'nahdi_discount',
#             'nahdi_ordered_qty'
#         ]

#         for col in numeric_columns:
#             if col in period_df.columns:
#                 period_df.loc[:, col] = pd.to_numeric(period_df[col].replace([None, 'N/A'], pd.NA), errors='coerce')

#         if product:
#             # Filter for the selected product
#             dff = period_df[period_df["Product"] == product]

#             dff.loc[:, numeric_columns] = dff[numeric_columns].replace([None, 'N/A'], pd.NA).apply(pd.to_numeric, errors='coerce')

#             # Fetch the competitor references for the selected product
#             from client_profile.models import Product
#             try:
#                 product_instance = Product.objects.get(TITLE=product)
#                 competitor_references = product_instance.competitor_references.all()
#                 competitor_reference_titles = [ref.TITLE for ref in competitor_references]
#             except Product.DoesNotExist:
#                 competitor_reference_titles = []

#             # Filter for category or subcategory match with key_name
#             categories = list(dff['Category'].dropna().unique())
#             subcategories = list(dff['Subcategory'].dropna().unique())

#             # Create competitor_df based on the filtered categories and subcategories for Competitor == True
#             competitor_df = period_df[
#                 # (period_df['Competitor'] == 'True') & 
#                 # (period_df['Category'].isin(categories) | period_df['Subcategory'].isin(subcategories))
#                 (period_df['Product'].isin(competitor_reference_titles))  
#             ]
#             competitor_df = competitor_df.sort_values(by=['Product', 'scraped_at'], ascending=[True, False])

#             # Filter bulk_df where key_name matches any Category or Subcategory in dff
#             bulk_df = period_df[period_df["key_name"].isin(categories + subcategories)]
#             bulk_df = bulk_df.sort_values(by=['nahdi_title', 'agregated_time'], ascending=[True, False])

#             # Prepare category_df and subcategory_df
#             category_df = bulk_df[bulk_df['key_name'].isin(categories)]
#             subcategory_df = bulk_df[bulk_df['key_name'].isin(subcategories)]

#             # Sort dff by Product and scraped_at
#             grouped_df = dff.sort_values(by=['Product', 'agregated_time'], ascending=[True, False])

#             # Debug: Save intermediate DataFrames to CSV for inspection
#             # grouped_df.to_csv('dff.csv')
#             # category_df.to_csv('category_df.csv')
#             # subcategory_df.to_csv('subcategory_df.csv')
#             # competitor_df.to_csv('competitor_df.csv')


        
#         fig = go.Figure()
#         competitor_fig = go.Figure()
#         competitor_style = {"display": "none"}  # Hide secondary graph by default

        

#         # Acount Price 
#         if plot_types == 'account_prices':
#             # Iterate over each account in selected_accounts
#             for account in selected_accounts:
#                 account_price_column = f"{account}_price"
#                 # Check if the account price column exists in grouped_df before plotting
#                 if account_price_column in grouped_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_df['agregated_time'],
#                         y=grouped_df[account_price_column],
#                         mode='lines',
#                         name=f"{account.capitalize()} Price"
#                     ))

#             if 'RSP_VAT' in grouped_df.columns:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['RSP_VAT'],
#                     mode='lines',
#                     name="RSP VAT",
#                     line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot')
#                 ))

#             # Calculate the average across the selected account columns
#             account_columns = []
#             if 'amazon' in selected_accounts and 'amazon_price' in grouped_df.columns:
#                 account_columns.append('amazon_price')
#             if 'nahdi' in selected_accounts and 'nahdi_price' in grouped_df.columns:
#                 account_columns.append('nahdi_price')
#             if 'dawa' in selected_accounts and 'dawa_price' in grouped_df.columns:
#                 account_columns.append('dawa_price')
#             if 'noon_sa' in selected_accounts and 'noon_sa_price' in grouped_df.columns:
#                 account_columns.append('noon_sa_price')

#             if account_columns:
#                 grouped_df["average_price"] = grouped_df[account_columns].mean(axis=1)
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df["average_price"],
#                     mode='lines',
#                     name="Average Price",
#                     line=dict(width=4, color='blue', dash='solid')
#                 ))

#             # Check if advanced overlay is set to "category"
#             if advanced_overlay and 'category' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_price_column = f"{account}_price"
                    
#                     # Ensure category_df is available and not empty
#                     if not category_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=category_df['agregated_time'],
#                             y=category_df[account_price_column],
#                             mode='markers',
#                             name=f"{account} - Category ({categories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=category_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for subcategory overlay.")

#             # Check if advanced overlay is set to "subcategory"
#             if advanced_overlay and 'subcategory' in advanced_overlay:

#                 for account in selected_accounts:
#                     account_price_column = f"{account}_price"
                    
#                     # Ensure category_df is available and not empty
#                     if not subcategory_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=subcategory_df['agregated_time'],
#                             y=subcategory_df[account_price_column],
#                             mode='markers',
#                             name=f"{account} - Subcategory ({subcategories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=subcategory_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for category overlay.")

#             # Check if advanced overlay is set to "OPPS"
#             if advanced_overlay and 'OPPS' in advanced_overlay:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['opps'],
#                     mode='lines',
#                     name="Online Price Performance Score",
#                     line=dict(width=4, color='red', dash='solid'),
#                     yaxis="y2"  # Assigning this trace to the secondary y-axis
#                 ))

#             # Check if advanced overlay is set to "competitor"
#             if advanced_overlay and 'competitor' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_price_column = f"{account}_price"

#                     # Add 'Product' as a column instead of an index
#                     competitor_df_grouped = competitor_df.groupby('Product').agg(
#                         avg_price=(account_price_column, 'mean'),
#                     )
#                     competitor_df_grouped = competitor_df_grouped.sort_values(by='avg_price', ascending=False)
#                     competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column


#                     # Calculate dynamic height for the chart
#                     chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
#                     # Create secondary figure for competitor analysis
#                     competitor_fig.add_trace(go.Bar(
#                         y=[label[:20] + "..." if len(label) > 20 else label for label in competitor_df_grouped['Product']],
#                         x=competitor_df_grouped['avg_price'],
#                         orientation='h',
#                         name= f'Average Price per Competitors for {account}',
#                         # marker=dict(color='rgba(255, 99, 71, 0.6)'),
#                         hovertext=competitor_df_grouped['Product'],  # Full product name for hover
#                         hoverinfo="text+x"  # Display both the hovertext and x-value

#                     ))

#                     competitor_fig.update_layout(
#                         title={
#                         'text': "Average Price Per Competitors",
#                         'y': 0.9,
#                         'x': 0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top'
#                     },

#                         xaxis_title="Price SAR",
#                         yaxis_title="Products",
#                         template="plotly_white",
#                         height=chart_height
#                     )

#                     # Make the secondary graph visible
#                     competitor_style = {"display": "block"}

#             # Update layout to include secondary y-axis
#             fig.update_layout(
#                 xaxis_title="Days",
#                 yaxis_title="Product Price SAR",  # Primary y-axis title
#                 yaxis2=dict(
#                     title="Online Price Performance Score",  # Secondary y-axis title
#                     overlaying="y",  # Overlay this axis on top of the primary y-axis
#                     side="right",  # Position the secondary y-axis on the right
#                     showgrid=False  # Optionally hide grid lines for the secondary axis
#                 ),
#                 title={
#                     'text': "Product Price Over Time",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },
#                 template="plotly_white",
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1
#                 )
#             )

#         # Promo Depth
#         if plot_types == 'promo_depth':
#             # Iterate over each account in selected_accounts
#             for account in selected_accounts:
#                 account_discount_column = f"{account}_discount"
#                 # Check if the account discount column exists in grouped_df before plotting
#                 if account_discount_column in grouped_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_df['agregated_time'],
#                         y=grouped_df[account_discount_column],
#                         mode='lines',
#                         name=f"{account.capitalize()} Discount"
#                     ))

#             if 'discount_percentage' in grouped_df.columns:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['discount_percentage'],
#                     mode='lines',
#                     name="Promo discount",
#                     line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot')
#                 ))

#             # Calculate the average across the selected account columns
#             account_columns = []
#             if 'amazon' in selected_accounts and 'amazon_discount' in grouped_df.columns:
#                 account_columns.append('amazon_discount')
#             if 'nahdi' in selected_accounts and 'nahdi_discount' in grouped_df.columns:
#                 account_columns.append('nahdi_discount')
#             if 'dawa' in selected_accounts and 'dawa_discount' in grouped_df.columns:
#                 account_columns.append('dawa_discount')
#             if 'noon_sa' in selected_accounts and 'noon_sa_discount' in grouped_df.columns:
#                 account_columns.append('noon_sa_discount')

#             if account_columns:
#                 grouped_df["average_discounts"] = grouped_df[account_columns].mean(axis=1)
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df["average_discounts"],
#                     mode='lines',
#                     name="Average Promo Discounts",
#                     line=dict(width=4, color='blue', dash='solid')
#                 ))

#             # Check if advanced overlay is set to "category"
#             if advanced_overlay and 'category' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_discount_column = f"{account}_discount"
#                     # Ensure category_df is available and not empty
#                     if not category_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=category_df['agregated_time'],
#                             y=category_df[account_discount_column],
#                             mode='markers',
#                             name=f"{account} - Category ({categories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=category_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for subcategory overlay.")

#             # Check if advanced overlay is set to "subcategory"
#             if advanced_overlay and 'subcategory' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_discount_column = f"{account}_discount"
#                     # Ensure category_df is available and not empty
#                     if not subcategory_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=subcategory_df['agregated_time'],
#                             y=subcategory_df[account_discount_column],
#                             mode='markers',
#                             name=f"{account} - Subcategory ({subcategories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=subcategory_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for Subcategory overlay.")

#             # Check if advanced overlay is set to "OPPS"
#             if advanced_overlay and 'OPPS' in advanced_overlay:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['opps'],
#                     mode='lines',
#                     name="Online Price Performance Score",
#                     line=dict(width=4, color='red', dash='solid'),
#                     yaxis="y2"  # Assigning this trace to the secondary y-axis
#                 ))

#             # Check if advanced overlay is set to "competitor"
#             if advanced_overlay and 'competitor' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_discount_column = f"{account}_discount"

#                     # Add 'Product' as a column instead of an index
#                     competitor_df_grouped = competitor_df.groupby('Product').agg(
#                         avg_promo=(account_discount_column, 'mean'),
#                     )
#                     competitor_df_grouped = competitor_df_grouped.sort_values(by='avg_promo', ascending=False)
#                     competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column


#                     # Calculate dynamic height for the chart
#                     chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
#                     # Create secondary figure for competitor analysis
#                     competitor_fig.add_trace(go.Bar(
#                         y=[label[:20] + "..." if len(label) > 20 else label for label in competitor_df_grouped['Product']],
#                         x=competitor_df_grouped['avg_promo'],
#                         orientation='h',
#                         name= f'Average Promo per Competitors for {account}',
#                         # marker=dict(color='rgba(255, 99, 71, 0.6)'),
#                         hovertext=competitor_df_grouped['Product'],  # Full product name for hover
#                         hoverinfo="text+x"  # Display both the hovertext and x-value

#                     ))

#                     competitor_fig.update_layout(
#                         title={
#                         'text': "Average Promo Per Competitors",
#                         'y': 0.9,
#                         'x': 0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top'
#                     },

#                         xaxis_title="Discount Percent",
#                         yaxis_title="Products",
#                         template="plotly_white",
#                         height=chart_height
#                     )

#                     # Make the secondary graph visible
#                     competitor_style = {"display": "block"}


#             # Update layout to include secondary y-axis
#             fig.update_layout(
#                 xaxis_title="Days",
#                 yaxis_title="Discount Percent",  # Primary y-axis title
#                 yaxis2=dict(
#                     title="Online Price Performance Score",  # Secondary y-axis title
#                     overlaying="y",  # Overlay this axis on top of the primary y-axis
#                     side="right",  # Position the secondary y-axis on the right
#                     showgrid=False  # Optionally hide grid lines for the secondary axis
#                 ),
#                 title={
#                     'text': "Promo Discount Over Time",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },
#                 template="plotly_white",
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1
#                 )
#             )

#         # Market Share 
#         if plot_types == 'market_share':

#             # Step 1: Shift 'nahdi_ordered_qty' by 1 within each product group
#             grouped_df['order_bfr'] = grouped_df['nahdi_ordered_qty'].shift(-1)

#             # Step 2: Calculate 'ordered_qty' as the difference between current and previous order quantity
#             grouped_df['ordered_qty'] = grouped_df['nahdi_ordered_qty'] -  grouped_df['order_bfr'] 
#             # grouped_df.to_csv('dff_calc.csv')
#             fig.add_trace(go.Bar(
#             x=grouped_df['agregated_time'],
#             y=grouped_df['ordered_qty'],
#             name='Total Order Quantity'
#         ))

#             # Add OPPS line if selected
#             if advanced_overlay and 'OPPS' in advanced_overlay :
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['opps'],
#                     mode='lines',
#                     name="Online Price Performance Score",
#                     line=dict(width=4, color='red', dash='solid'),
#                     yaxis="y2"  # Assigning this trace to the secondary y-axis
#                 ))

#             fig.update_layout(
#                 xaxis_title="Days",
#                 yaxis_title="Unit Solds",  # Primary y-axis title
#                 yaxis2=dict(
#                     title="Online Price Performance Score",  # Secondary y-axis title
#                     overlaying="y",  # Overlay this axis on top of the primary y-axis
#                     side="right",  # Position the secondary y-axis on the right
#                     showgrid=False  # Optionally hide grid lines for the secondary axis
#                 ),
#                 title={
#                     'text': "Market Share Analysis: Order Quantity Per Selected Period",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },
#                 template="plotly_white",
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1

#                 )
#             )

            
#             if advanced_overlay and 'competitor' in advanced_overlay:
#                 # Add 'Product' as a column instead of an index
#                 competitor_df_grouped = competitor_df.groupby('Product').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
#                 competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
#                 competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column

#                 # Similarly for product_grouped
#                 product_grouped = dff.groupby('Product').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 product_grouped['unit_sold'] = product_grouped['max_ordered_qty'] - product_grouped['min_ordered_qty']
#                 product_grouped = product_grouped.reset_index()  # Reset index to make 'Product' a column

#                 # Concatenate the two DataFrames
#                 combined_df = pd.concat([product_grouped, competitor_df_grouped], ignore_index=True)
#                 # combined_df.to_csv('combined_df.csv')
#                 # dff.to_csv('dff.csv')
#                 # product_grouped.to_csv('product_grouped.csv')
#                 # Calculate dynamic height for the chart
#                 chart_height = max(400, len(combined_df) * 30)  # Minimum 400px, 30px per bar
#                 # Create secondary figure for competitor analysis
#                 competitor_fig.add_trace(go.Bar(
#                     y=[label[:20] + "..." if len(label) > 20 else label for label in combined_df['Product']],
#                     x=combined_df['unit_sold'],
#                     orientation='h',
#                     name='Unit Sold per Competitor',
#                     marker=dict(color='rgba(255, 99, 71, 0.6)'),
#                     hovertext=combined_df['Product'],  # Full product name for hover
#                     hoverinfo="text+x"  # Display both the hovertext and x-value

#                 ))

#                 competitor_fig.update_layout(
#                     title={
#                     'text': "Market Share Analysis",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },

#                     xaxis_title="Unit Sold",
#                     yaxis_title="Products",
#                     template="plotly_white",
#                     height=chart_height
#                 )

#                 # Make the secondary graph visible
#                 competitor_style = {"display": "block"}


#             if advanced_overlay and 'category' in advanced_overlay:
#                 # Add 'Product' as a column instead of an index
#                 competitor_df_grouped = category_df.groupby('nahdi_title').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
#                 competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
#                 competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column
#                 # Calculate dynamic height for the chart
#                 chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
                
#                 # Create unique y labels to handle duplicate initial characters
#                 competitor_df_grouped['unique_label'] = [
#                     f"{label[:20]}... ({i})" if len(label) > 20 else f"{label} ({i})"
#                     for i, label in enumerate(competitor_df_grouped['nahdi_title'], start=1)
#                 ]


#                 # Create secondary figure for competitor analysis
#                 competitor_fig.add_trace(go.Bar(
#                     y=competitor_df_grouped['unique_label'],  # Use unique y labels
#                     x=competitor_df_grouped['unit_sold'],
#                     orientation='h',
#                     name=f'Unit Sold per Category {categories}',
#                     marker=dict(
#                         color='rgba(75, 192, 192, 0.6)',  # Alternate color
#                     ),
#                     hovertext=competitor_df_grouped['nahdi_title'],  # Full product name for hover
#                     hoverinfo="text+x"  # Display both the hovertext and x-value

#                 ))

#                 competitor_fig.update_layout(
#                     title={
#                         'text': "Market Share Analysis",
#                         'y': 0.9,
#                         'x': 0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top'
#                     },
#                     xaxis_title="Unit Sold",
#                     yaxis_title="Products",
#                     yaxis=dict(
#                         showticklabels=False,  # Hide y-axis tick labels
#                         showgrid=False  # Hide grid lines for y-axis
#                     ),
#                     template="plotly_white",
#                     height=chart_height,  # Set dynamic height
#                 )

#                 # Make the secondary graph visible
#                 competitor_style = {"display": "block"}


#             if advanced_overlay and 'subcategory' in advanced_overlay:
#                 # Add 'Product' as a column instead of an index
#                 competitor_df_grouped = subcategory_df.groupby('nahdi_title').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
#                 competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
#                 competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column

#                 # Calculate dynamic height for the chart
#                 chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
#                                 # Create unique y labels to handle duplicate initial characters
#                 competitor_df_grouped['unique_label'] = [
#                     f"{label[:20]}... ({i})" if len(label) > 20 else f"{label} ({i})"
#                     for i, label in enumerate(competitor_df_grouped['nahdi_title'], start=1)
#                 ]

#                 # Create secondary figure for competitor analysis
#                 competitor_fig.add_trace(go.Bar(
#                     y=competitor_df_grouped['unique_label'],  # Use unique y labels
#                     x=competitor_df_grouped['unit_sold'],
#                     orientation='h',
#                     name=f'Unit Sold per Subcategory {subcategories}',
#                     marker=dict(color='rgba(153, 102, 255, 0.6)'),
#                     hovertext=competitor_df_grouped['nahdi_title'],  # Full product name for hover
#                     hoverinfo="text+x"  # Display both the hovertext and x-value

#                 ))

#                 competitor_fig.update_layout(
#                     title={
#                     'text': "Market Share Analysis",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },

#                     xaxis_title="Unit Sold",
#                     yaxis_title="Products",
#                     yaxis=dict(
#                         showticklabels=False,  # Hide y-axis tick labels
#                         showgrid=False  # Hide grid lines for y-axis
#                     ),                    template="plotly_white",
#                     height=chart_height
#                 )

#                 # Make the secondary graph visible
#                 competitor_style = {"display": "block"}


#         return fig, competitor_fig, competitor_style

#     return app

# # Old function changed on 14/Jan
# def plot_dashboard(serialized_data, user_accounts):
#     # Debug: Confirm serialized_data is in JSON format
#     if isinstance(serialized_data, dict):
#         raise TypeError("serialized_data must be JSON, not a Python dictionary")

#     # Deserialize JSON data
#     data = json.loads(serialized_data)

#     # Debug: Print lengths of data fields
#     # for key, value in data.items():
#     #     print(f"{key}: {len(value)}")

#     # Create DataFrame
#     df = pd.DataFrame(data)

#     # Parse datetime fields
#     if 'scraped_at' in df.columns:
#         df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')

#     # Debug: Print DataFrame info
#     # print(df.infos())
#     df['scraped_at'] = pd.to_datetime(df['scraped_at'], errors='coerce')
#     # df.sample(frac =.10).to_csv('df_main_tailafter.csv')
#     # print('Competitor are',df['Competitor'].unique())
#     # print('Competitor afalse',df[df['Competitor'] == 'False']['Product'].unique())

#     app = DjangoDash('OPPS_Line', external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

#     app.layout = html.Div(
#         [
#             html.Div([
#                 html.Div([
#                     html.H5("Product", className='pt-4'),
#                     dcc.Dropdown(
#                         id="product",
#                         # options=[{"label": i, "value": i} for i in sorted(df["Product"].unique())],
#                         options=[{"label": i, "value": i} for i in sorted(filter(lambda x: x is not None, df[df['Competitor'] == 'False']["Product"].unique()))],
#                         value=None,
#                         multi=False
#                     ),
#                     html.H5("Period", className='pt-4'),
#                     dcc.Dropdown(
#                         id="period",
#                         options=[
#                             {"label": "Last Week", "value": "last_week"},
#                             {"label": "Last Month", "value": "last_month"},
#                             {"label": "Last 6 Months", "value": "last_6_months"},
#                             {"label": "Last Year", "value": "last_year"},
#                             {"label": "Year to Date", "value": "ytd"}
#                         ],
#                         value="last_week",
#                         multi=False
#                     ),
#                     html.H5("Account", className='pt-4'),
#                     dcc.Dropdown(
#                         id="account",
#                         options=[{"label": account, "value": account} for account in user_accounts],
#                         value=None,
#                         multi=True
#                     ),
#                     html.H5("Plot Type", className='pt-4'),
#                     dcc.Dropdown(
#                         id="plot-types",
#                         options=[
#                             {"label": "Account Prices", "value": "account_prices"},
#                             {"label": "Promo Depth", "value": "promo_depth"},
#                             {"label": "Market Sahre", "value": "market_share"},
#                         ],
#                         value=None,
#                         multi=False
#                     ),
#                     # Advanced Overlay Dropdown
#                     html.H5("Advanced Overlay", className='pt-4', id='overlay-header'),
#                     dcc.Dropdown(
#                         id="advanced-overlay",
#                         options=[
#                             {"label": "Category", "value": "category"},
#                             {"label": "Subcategory", "value": "subcategory"},
#                             {"label": "Competitor", "value": "competitor"},
#                             {"label": "Online Price Performance Score", "value": "OPPS"},
#                         ],
#                         value=None,
#                         multi=True
#                     ),
#                 ], className='card-body p-3'),
#             ], className='container-fluid'),

#             html.Div([
#                 html.Div([
#                     # html.H4("Online Price Performance Score Over Time (Grouped by 6-hour Intervals)", className='card-header pb-0'),
#                     html.Div([
#                         dcc.Graph(id="line"),
#                     ]),
#                 ], className='card-body p-3'),
#                     html.Div([
#                         dcc.Graph(id="competitor-graph", style={"display": "none"}),  # Secondary graph
#                     ], className='card-body p-3'),
#             ], className='container-fluid'),
#         ], className='container-fluid'
#     )

#     # Callback to toggle the visibility of the advanced overlay dropdown
#     @app.callback(
#         Output('advanced-overlay', 'style'),
#         Output('overlay-header', 'style'),
#         Input('plot-types', 'value')
#     )
#     def toggle_advanced_overlay(plot_types):
#         if plot_types in ["account_prices", "market_share", "promo_depth"]:
#             return {'display': 'block'}, {'display': 'block'}  # Show overlay dropdown and header
#         return {'display': 'none'}, {'display': 'none'}  # Hide overlay dropdown and header

#     # @app.callback(
#     #     Output("line", "figure"),
#     #     Input("product", "value"),
#     #     Input("period", "value"),
#     #     Input("account", "value"),
#     #     Input("plot-types", "value"),
#     #     Input("advanced-overlay", "value")  # Added advanced overlay input
#     # )

#     @app.callback(
#     [
#         Output("line", "figure"),  # Primary graph
#         Output("competitor-graph", "figure"),  # Secondary graph
#         Output("competitor-graph", "style"),  # Secondary graph visibility
#     ],
#     [
#         Input("product", "value"),
#         Input("period", "value"),
#         Input("account", "value"),
#         Input("plot-types", "value"),
#         Input("advanced-overlay", "value")  # Advanced overlay input
#     ]
# )



#     def update_line_chart(product, period, selected_accounts, plot_types, advanced_overlay):
#         # Initial debug statement to confirm callback input values
#         print(f"Product: {product}, Period: {period}, Accounts: {selected_accounts}, Plot Type: {plot_types}, Overlay: {advanced_overlay}")

#         if selected_accounts is None:
#             selected_accounts = []

#         df_copy = copy.deepcopy(df)

#         # Ensure scraped_at is in datetime format
#         df_copy['scraped_at'] = pd.to_datetime(df_copy['scraped_at'], errors='coerce').dt.tz_localize(None)

#         # Check for any NaT values after conversion
#         if df_copy['scraped_at'].isnull().any():
#             raise ValueError("There are invalid dates in the scraped_at column.")

#         if product:
#             # Filter for the selected product
#             df_product = df_copy[df_copy["Product"] == product]

#             # Ensure numeric columns are cleaned and converted
#             numeric_columns = ['amazon_price', 
#                                'nahdi_price', 
#                                'dawa_price',
#                                'noon_sa_price', 
#                                'amazon_discount', 
#                                'dawa_discount', 
#                                'noon_sa_discount',
#                                'nahdi_discount', 
#                                'nahdi_ordered_qty']
#             df_product.loc[:, numeric_columns] = df_product[numeric_columns].replace([None, 'N/A'], pd.NA).apply(pd.to_numeric, errors='coerce')
#             # print('dtypes are', df_product.dtypes)
#             # Filter for category or subcategory match with key_name
#             categories = list(df_product['Category'].dropna().unique())
#             subcategories = list(df_product['Subcategory'].dropna().unique())

#             # print("Categories:", df_product['Category'].unique())
#             # print("Subcategories:", df_product['Subcategory'].unique())

#             # Create competitor_df based on the filtered categories and subcategories for Competitor == True
#             competitor_df = df_copy[
#                 (df_copy['Competitor'] == 'True') & 
#                 (df_copy['Category'].isin(categories) | df_copy['Subcategory'].isin(subcategories))
#             ]
#             competitor_df = competitor_df.sort_values(by=['Product', 'scraped_at'], ascending=[True, False])

#             # Filter bulk_df where key_name matches any Category or Subcategory in df_product
#             bulk_df = df_copy[df_copy["key_name"].isin(categories + subcategories)]
#             bulk_df = bulk_df.sort_values(by=['nahdi_title', 'scraped_at'], ascending=[True, False])
#             # bulk_df.to_csv('bulk_df_before_agg.csv')

#             # Sort by Product and scraped_at
#             dff = df_product.sort_values(by=['Product', 'scraped_at'], ascending=[True, False])
#             # dff.to_csv('dff_before_agg.csv')

#             # Set end and start dates for filtering
#             end_date = dff['scraped_at'].max()
#             if pd.isna(end_date):  # If end_date is NaT
#                 raise ValueError("End date could not be determined. Please check your data.")


#             # Period selection logic
#             if period == "last_week":
#                 start_date = end_date - pd.DateOffset(weeks=1)
#                 floor_interval = '12h'
#                 # bin_num = 14  # Approx 2 bins per day
#             elif period == "last_month":
#                 start_date = end_date - pd.DateOffset(months=1)
#                 floor_interval = 'D'
#                 # bin_num = 30  # Approx 2 bins per day
#             elif period == "last_6_months":
#                 start_date = end_date - pd.DateOffset(months=6)
#                 floor_interval = 'W-MON'  # Use custom weekly handling below
#                 # bin_num = 26  # Approx 2 bins per day
#             elif period == "last_year":
#                 start_date = end_date - pd.DateOffset(years=1)
#                 floor_interval = 'M'  # Set to monthly
#                 # bin_num = 12  # Monthly bins for one year
#             elif period == "ytd":
#                 current_year = pd.Timestamp.now().year
#                 start_date = pd.Timestamp(f'{current_year}-01-01')  # Start of the current year
#                 floor_interval = 'M'  # Set to monthly
#                 # bin_num = (end_date - start_date).days // 30  # Approx monthly bins for YTD
#             else:
#                 raise ValueError(f"Invalid period: {period}. Please choose a valid period.")  # Catch invalid periods

#             # Additional check for start_date being None
#             if start_date is None:
#                 raise ValueError("Start date could not be determined. Please check your period logic.")  # Fail gracefully

#             # Check if end_date is valid
#             if pd.isna(end_date):  # If end_date is NaT
#                 raise ValueError("End date could not be determined. Please check your data.")


#             start_date = start_date.tz_localize(None) if start_date and start_date.tzinfo else start_date
#             end_date = end_date.tz_localize(None) if end_date and end_date.tzinfo else end_date

#             # Calculate dynamic bar width in milliseconds
#             # total_duration = (end_date - start_date).total_seconds() * 1000  # in milliseconds
#             # bar_width = total_duration / bin_num if bin_num else 86400 * 1000  # default to 1 day if bin_num is not set

#             # Filter by date range and clean up data
#             dff = dff[(dff['scraped_at'] >= start_date) & (dff['scraped_at'] <= end_date)]
#             competitor_df = competitor_df[(competitor_df['scraped_at'] >= start_date) & (competitor_df['scraped_at'] <= end_date)]
#             # prepare the Bulk_df for category and subcategory
#             category_df = bulk_df[bulk_df['key_name'].isin(categories)]
#             category_df = category_df[(category_df['scraped_at'] >= start_date) & (category_df['scraped_at'] <= end_date)]
#             subcategory_df = bulk_df[bulk_df['key_name'].isin(subcategories)]
#             subcategory_df = subcategory_df[(subcategory_df['scraped_at'] >= start_date) & (subcategory_df['scraped_at'] <= end_date)]

#             # Custom grouping for 6 months (weekly intervals within months)
#             if period == "last_6_months":
#                 # Add week of the month for dff, category_df, and subcategory_df
#                 for dataframe in [dff, category_df, subcategory_df, competitor_df]:
#                     dataframe['week_of_month'] = dataframe['scraped_at'].apply(lambda x: (x.day - 1) // 7 + 1)
#                     dataframe['agregated_time'] = dataframe['scraped_at'].dt.to_period("M").astype(str) + "_W" + dataframe['week_of_month'].astype(str)

#             # Monthly aggregation for yearly data
#             elif period == "last_year":
#                 for dataframe in [dff, category_df, subcategory_df, competitor_df]:
#                     dataframe['agregated_time'] = dataframe['scraped_at'].dt.to_period("M").astype(str)

#             # Monthly aggregation for yearly data starts from January (YTY)
#             elif period == "ytd":
#                 for dataframe in [dff, category_df, subcategory_df, competitor_df]:
#                     dataframe['agregated_time'] = dataframe['scraped_at'].dt.to_period('M').astype(str)

#             else:
#                 # For other periods, floor the date by the selected interval
#                 for dataframe in [dff, category_df, subcategory_df, competitor_df]:
#                     dataframe['agregated_time'] = dataframe['scraped_at'].dt.floor(floor_interval)

#             # Group by the aggregated time and calculate the mean
#             grouped_df = dff.groupby('agregated_time').agg({
#                 'amazon_price': 'mean',
#                 'nahdi_price': 'mean',
#                 'dawa_price': 'mean',
#                 'noon_sa_price': 'mean',
#                 'amazon_discount': 'mean',
#                 'dawa_discount': 'mean',
#                 'nahdi_discount': 'mean',
#                 'noon_sa_discount': 'mean',
#                 'RSP_VAT': 'mean',
#                 'discount_percentage': 'mean',
#                 'opps': 'mean',
#                 'nahdi_ordered_qty': 'max'
#             }).reset_index()
#             # grouped_df.to_csv('dff_after_agg.csv')



        
#         fig = go.Figure()
#         competitor_fig = go.Figure()
#         competitor_style = {"display": "none"}  # Hide secondary graph by default

        

#         # Acount Price 
#         if plot_types == 'account_prices':
#             # Iterate over each account in selected_accounts
#             for account in selected_accounts:
#                 account_price_column = f"{account}_price"
#                 # Check if the account price column exists in grouped_df before plotting
#                 if account_price_column in grouped_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_df['agregated_time'],
#                         y=grouped_df[account_price_column],
#                         mode='lines',
#                         name=f"{account.capitalize()} Price"
#                     ))

#             if 'RSP_VAT' in grouped_df.columns:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['RSP_VAT'],
#                     mode='lines',
#                     name="RSP VAT",
#                     line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot')
#                 ))

#             # Calculate the average across the selected account columns
#             account_columns = []
#             if 'amazon' in selected_accounts and 'amazon_price' in grouped_df.columns:
#                 account_columns.append('amazon_price')
#             if 'nahdi' in selected_accounts and 'nahdi_price' in grouped_df.columns:
#                 account_columns.append('nahdi_price')
#             if 'dawa' in selected_accounts and 'dawa_price' in grouped_df.columns:
#                 account_columns.append('dawa_price')
#             if 'noon_sa' in selected_accounts and 'noon_sa_price' in grouped_df.columns:
#                 account_columns.append('noon_sa_price')

#             if account_columns:
#                 grouped_df["average_price"] = grouped_df[account_columns].mean(axis=1)
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df["average_price"],
#                     mode='lines',
#                     name="Average Price",
#                     line=dict(width=4, color='blue', dash='solid')
#                 ))

#             # Check if advanced overlay is set to "category"
#             if advanced_overlay and 'category' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_price_column = f"{account}_price"
                    
#                     # Ensure category_df is available and not empty
#                     if not category_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=category_df['agregated_time'],
#                             y=category_df[account_price_column],
#                             mode='markers',
#                             name=f"{account} - Category ({categories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=category_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for subcategory overlay.")

#             # Check if advanced overlay is set to "subcategory"
#             if advanced_overlay and 'subcategory' in advanced_overlay:

#                 for account in selected_accounts:
#                     account_price_column = f"{account}_price"
                    
#                     # Ensure category_df is available and not empty
#                     if not subcategory_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=subcategory_df['agregated_time'],
#                             y=subcategory_df[account_price_column],
#                             mode='markers',
#                             name=f"{account} - Subcategory ({subcategories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=subcategory_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for category overlay.")

#             # Check if advanced overlay is set to "OPPS"
#             if advanced_overlay and 'OPPS' in advanced_overlay:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['opps'],
#                     mode='lines',
#                     name="Online Price Performance Score",
#                     line=dict(width=4, color='red', dash='solid'),
#                     yaxis="y2"  # Assigning this trace to the secondary y-axis
#                 ))

#             # Check if advanced overlay is set to "competitor"
#             if advanced_overlay and 'competitor' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_price_column = f"{account}_price"

#                     # Add 'Product' as a column instead of an index
#                     competitor_df_grouped = competitor_df.groupby('Product').agg(
#                         avg_price=(account_price_column, 'mean'),
#                     )
#                     competitor_df_grouped = competitor_df_grouped.sort_values(by='avg_price', ascending=False)
#                     competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column


#                     # Calculate dynamic height for the chart
#                     chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
#                     # Create secondary figure for competitor analysis
#                     competitor_fig.add_trace(go.Bar(
#                         y=[label[:20] + "..." if len(label) > 20 else label for label in competitor_df_grouped['Product']],
#                         x=competitor_df_grouped['avg_price'],
#                         orientation='h',
#                         name= f'Average Price per Competitors for {account}',
#                         # marker=dict(color='rgba(255, 99, 71, 0.6)'),
#                         hovertext=competitor_df_grouped['Product'],  # Full product name for hover
#                         hoverinfo="text+x"  # Display both the hovertext and x-value

#                     ))

#                     competitor_fig.update_layout(
#                         title={
#                         'text': "Average Price Per Competitors",
#                         'y': 0.9,
#                         'x': 0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top'
#                     },

#                         xaxis_title="Price SAR",
#                         yaxis_title="Products",
#                         template="plotly_white",
#                         height=chart_height
#                     )

#                     # Make the secondary graph visible
#                     competitor_style = {"display": "block"}

#             # Update layout to include secondary y-axis
#             fig.update_layout(
#                 xaxis_title="Days",
#                 yaxis_title="Product Price SAR",  # Primary y-axis title
#                 yaxis2=dict(
#                     title="Online Price Performance Score",  # Secondary y-axis title
#                     overlaying="y",  # Overlay this axis on top of the primary y-axis
#                     side="right",  # Position the secondary y-axis on the right
#                     showgrid=False  # Optionally hide grid lines for the secondary axis
#                 ),
#                 title={
#                     'text': "Product Price Over Time",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },
#                 template="plotly_white",
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1
#                 )
#             )

#         # Promo Depth
#         if plot_types == 'promo_depth':
#             # Iterate over each account in selected_accounts
#             for account in selected_accounts:
#                 account_discount_column = f"{account}_discount"
#                 # Check if the account discount column exists in grouped_df before plotting
#                 if account_discount_column in grouped_df.columns:
#                     fig.add_trace(go.Scatter(
#                         x=grouped_df['agregated_time'],
#                         y=grouped_df[account_discount_column],
#                         mode='lines',
#                         name=f"{account.capitalize()} Discount"
#                     ))

#             if 'discount_percentage' in grouped_df.columns:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['discount_percentage'],
#                     mode='lines',
#                     name="Promo discount",
#                     line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot')
#                 ))

#             # Calculate the average across the selected account columns
#             account_columns = []
#             if 'amazon' in selected_accounts and 'amazon_discount' in grouped_df.columns:
#                 account_columns.append('amazon_discount')
#             if 'nahdi' in selected_accounts and 'nahdi_discount' in grouped_df.columns:
#                 account_columns.append('nahdi_discount')
#             if 'dawa' in selected_accounts and 'dawa_discount' in grouped_df.columns:
#                 account_columns.append('dawa_discount')
#             if 'noon_sa' in selected_accounts and 'noon_sa_discount' in grouped_df.columns:
#                 account_columns.append('noon_sa_discount')

#             if account_columns:
#                 grouped_df["average_discounts"] = grouped_df[account_columns].mean(axis=1)
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df["average_discounts"],
#                     mode='lines',
#                     name="Average Promo Discounts",
#                     line=dict(width=4, color='blue', dash='solid')
#                 ))

#             # Check if advanced overlay is set to "category"
#             if advanced_overlay and 'category' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_discount_column = f"{account}_discount"
#                     # Ensure category_df is available and not empty
#                     if not category_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=category_df['agregated_time'],
#                             y=category_df[account_discount_column],
#                             mode='markers',
#                             name=f"{account} - Category ({categories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=category_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for subcategory overlay.")

#             # Check if advanced overlay is set to "subcategory"
#             if advanced_overlay and 'subcategory' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_discount_column = f"{account}_discount"
#                     # Ensure category_df is available and not empty
#                     if not subcategory_df.empty:
#                         # Add scatter plot for the category_df data
#                         fig.add_trace(go.Scatter(
#                             x=subcategory_df['agregated_time'],
#                             y=subcategory_df[account_discount_column],
#                             mode='markers',
#                             name=f"{account} - Subcategory ({subcategories})",
#                             marker=dict(size=8, symbol='circle'),
#                             text=subcategory_df[f"{account}_title"],  # Add the account_title to display on hover
#                             hoverinfo='text',  # Show the 'text' value on hover
#                         ))
#                     else:
#                         print(f"No data found for Subcategory overlay.")

#             # Check if advanced overlay is set to "OPPS"
#             if advanced_overlay and 'OPPS' in advanced_overlay:
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['opps'],
#                     mode='lines',
#                     name="Online Price Performance Score",
#                     line=dict(width=4, color='red', dash='solid'),
#                     yaxis="y2"  # Assigning this trace to the secondary y-axis
#                 ))

#             # Check if advanced overlay is set to "competitor"
#             if advanced_overlay and 'competitor' in advanced_overlay:
#                 for account in selected_accounts:
#                     account_discount_column = f"{account}_discount"

#                     # Add 'Product' as a column instead of an index
#                     competitor_df_grouped = competitor_df.groupby('Product').agg(
#                         avg_promo=(account_discount_column, 'mean'),
#                     )
#                     competitor_df_grouped = competitor_df_grouped.sort_values(by='avg_promo', ascending=False)
#                     competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column


#                     # Calculate dynamic height for the chart
#                     chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
#                     # Create secondary figure for competitor analysis
#                     competitor_fig.add_trace(go.Bar(
#                         y=[label[:20] + "..." if len(label) > 20 else label for label in competitor_df_grouped['Product']],
#                         x=competitor_df_grouped['avg_promo'],
#                         orientation='h',
#                         name= f'Average Promo per Competitors for {account}',
#                         # marker=dict(color='rgba(255, 99, 71, 0.6)'),
#                         hovertext=competitor_df_grouped['Product'],  # Full product name for hover
#                         hoverinfo="text+x"  # Display both the hovertext and x-value

#                     ))

#                     competitor_fig.update_layout(
#                         title={
#                         'text': "Average Promo Per Competitors",
#                         'y': 0.9,
#                         'x': 0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top'
#                     },

#                         xaxis_title="Discount Percent",
#                         yaxis_title="Products",
#                         template="plotly_white",
#                         height=chart_height
#                     )

#                     # Make the secondary graph visible
#                     competitor_style = {"display": "block"}


#             # Update layout to include secondary y-axis
#             fig.update_layout(
#                 xaxis_title="Days",
#                 yaxis_title="Discount Percent",  # Primary y-axis title
#                 yaxis2=dict(
#                     title="Online Price Performance Score",  # Secondary y-axis title
#                     overlaying="y",  # Overlay this axis on top of the primary y-axis
#                     side="right",  # Position the secondary y-axis on the right
#                     showgrid=False  # Optionally hide grid lines for the secondary axis
#                 ),
#                 title={
#                     'text': "Promo Discount Over Time",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },
#                 template="plotly_white",
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1
#                 )
#             )

#         # Market Share 
#         if plot_types == 'market_share':

#             # Step 1: Shift 'nahdi_ordered_qty' by 1 within each product group
#             grouped_df['order_bfr'] = grouped_df['nahdi_ordered_qty'].shift(+1)

#             # Step 2: Calculate 'ordered_qty' as the difference between current and previous order quantity
#             grouped_df['ordered_qty'] = grouped_df['nahdi_ordered_qty'] -  grouped_df['order_bfr'] 
#             # grouped_df.to_csv('dff_calc.csv')
#             fig.add_trace(go.Bar(
#             x=grouped_df['agregated_time'],
#             y=grouped_df['ordered_qty'],
#             name='Total Order Quantity'
#         ))

#             # Add OPPS line if selected
#             if advanced_overlay and 'OPPS' in advanced_overlay :
#                 fig.add_trace(go.Scatter(
#                     x=grouped_df['agregated_time'],
#                     y=grouped_df['opps'],
#                     mode='lines',
#                     name="Online Price Performance Score",
#                     line=dict(width=4, color='red', dash='solid'),
#                     yaxis="y2"  # Assigning this trace to the secondary y-axis
#                 ))

#             fig.update_layout(
#                 xaxis_title="Days",
#                 yaxis_title="Unit Solds",  # Primary y-axis title
#                 yaxis2=dict(
#                     title="Online Price Performance Score",  # Secondary y-axis title
#                     overlaying="y",  # Overlay this axis on top of the primary y-axis
#                     side="right",  # Position the secondary y-axis on the right
#                     showgrid=False  # Optionally hide grid lines for the secondary axis
#                 ),
#                 title={
#                     'text': "Market Share Analysis: Order Quantity Per Selected Period",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },
#                 template="plotly_white",
#                 legend=dict(
#                     orientation="h",
#                     yanchor="bottom",
#                     y=1.02,
#                     xanchor="right",
#                     x=1

#                 )
#             )

            
#             if advanced_overlay and 'competitor' in advanced_overlay:
#                 # Add 'Product' as a column instead of an index
#                 competitor_df_grouped = competitor_df.groupby('Product').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
#                 competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
#                 competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column

#                 # Similarly for product_grouped
#                 product_grouped = dff.groupby('Product').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 product_grouped['unit_sold'] = product_grouped['max_ordered_qty'] - product_grouped['min_ordered_qty']
#                 product_grouped = product_grouped.reset_index()  # Reset index to make 'Product' a column

#                 # Concatenate the two DataFrames
#                 combined_df = pd.concat([product_grouped, competitor_df_grouped], ignore_index=True)
#                 # combined_df.to_csv('combined_df.csv')
#                 # dff.to_csv('dff.csv')
#                 # product_grouped.to_csv('product_grouped.csv')
#                 # Calculate dynamic height for the chart
#                 chart_height = max(400, len(combined_df) * 30)  # Minimum 400px, 30px per bar
#                 # Create secondary figure for competitor analysis
#                 competitor_fig.add_trace(go.Bar(
#                     y=[label[:20] + "..." if len(label) > 20 else label for label in combined_df['Product']],
#                     x=combined_df['unit_sold'],
#                     orientation='h',
#                     name='Unit Sold per Competitor',
#                     marker=dict(color='rgba(255, 99, 71, 0.6)'),
#                     hovertext=combined_df['Product'],  # Full product name for hover
#                     hoverinfo="text+x"  # Display both the hovertext and x-value

#                 ))

#                 competitor_fig.update_layout(
#                     title={
#                     'text': "Market Share Analysis",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },

#                     xaxis_title="Unit Sold",
#                     yaxis_title="Products",
#                     template="plotly_white",
#                     height=chart_height
#                 )

#                 # Make the secondary graph visible
#                 competitor_style = {"display": "block"}


#             if advanced_overlay and 'category' in advanced_overlay:
#                 # Add 'Product' as a column instead of an index
#                 competitor_df_grouped = category_df.groupby('nahdi_title').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
#                 competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
#                 competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column
#                 # Calculate dynamic height for the chart
#                 chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
                
#                 # Create unique y labels to handle duplicate initial characters
#                 competitor_df_grouped['unique_label'] = [
#                     f"{label[:20]}... ({i})" if len(label) > 20 else f"{label} ({i})"
#                     for i, label in enumerate(competitor_df_grouped['nahdi_title'], start=1)
#                 ]


#                 # Create secondary figure for competitor analysis
#                 competitor_fig.add_trace(go.Bar(
#                     y=competitor_df_grouped['unique_label'],  # Use unique y labels
#                     x=competitor_df_grouped['unit_sold'],
#                     orientation='h',
#                     name=f'Unit Sold per Category {categories}',
#                     marker=dict(
#                         color='rgba(75, 192, 192, 0.6)',  # Alternate color
#                     ),
#                     hovertext=competitor_df_grouped['nahdi_title'],  # Full product name for hover
#                     hoverinfo="text+x"  # Display both the hovertext and x-value

#                 ))

#                 competitor_fig.update_layout(
#                     title={
#                         'text': "Market Share Analysis",
#                         'y': 0.9,
#                         'x': 0.5,
#                         'xanchor': 'center',
#                         'yanchor': 'top'
#                     },
#                     xaxis_title="Unit Sold",
#                     yaxis_title="Products",
#                     yaxis=dict(
#                         showticklabels=False,  # Hide y-axis tick labels
#                         showgrid=False  # Hide grid lines for y-axis
#                     ),
#                     template="plotly_white",
#                     height=chart_height,  # Set dynamic height
#                 )

#                 # Make the secondary graph visible
#                 competitor_style = {"display": "block"}


#             if advanced_overlay and 'subcategory' in advanced_overlay:
#                 # Add 'Product' as a column instead of an index
#                 competitor_df_grouped = subcategory_df.groupby('nahdi_title').agg(
#                     max_ordered_qty=('nahdi_ordered_qty', 'max'),
#                     min_ordered_qty=('nahdi_ordered_qty', 'min')
#                 )
#                 competitor_df_grouped['unit_sold'] = competitor_df_grouped['max_ordered_qty'] - competitor_df_grouped['min_ordered_qty']
#                 competitor_df_grouped = competitor_df_grouped.sort_values(by='unit_sold', ascending=False)
#                 competitor_df_grouped = competitor_df_grouped.reset_index()  # Reset index to make 'Product' a column

#                 # Calculate dynamic height for the chart
#                 chart_height = max(400, len(competitor_df_grouped) * 30)  # Minimum 400px, 30px per bar
#                                 # Create unique y labels to handle duplicate initial characters
#                 competitor_df_grouped['unique_label'] = [
#                     f"{label[:20]}... ({i})" if len(label) > 20 else f"{label} ({i})"
#                     for i, label in enumerate(competitor_df_grouped['nahdi_title'], start=1)
#                 ]

#                 # Create secondary figure for competitor analysis
#                 competitor_fig.add_trace(go.Bar(
#                     y=competitor_df_grouped['unique_label'],  # Use unique y labels
#                     x=competitor_df_grouped['unit_sold'],
#                     orientation='h',
#                     name=f'Unit Sold per Subcategory {subcategories}',
#                     marker=dict(color='rgba(153, 102, 255, 0.6)'),
#                     hovertext=competitor_df_grouped['nahdi_title'],  # Full product name for hover
#                     hoverinfo="text+x"  # Display both the hovertext and x-value

#                 ))

#                 competitor_fig.update_layout(
#                     title={
#                     'text': "Market Share Analysis",
#                     'y': 0.9,
#                     'x': 0.5,
#                     'xanchor': 'center',
#                     'yanchor': 'top'
#                 },

#                     xaxis_title="Unit Sold",
#                     yaxis_title="Products",
#                     yaxis=dict(
#                         showticklabels=False,  # Hide y-axis tick labels
#                         showgrid=False  # Hide grid lines for y-axis
#                     ),                    template="plotly_white",
#                     height=chart_height
#                 )

#                 # Make the secondary graph visible
#                 competitor_style = {"display": "block"}


#         return fig, competitor_fig, competitor_style

#     return app

