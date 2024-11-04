
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import pandas as pd
from dash import dcc, html, Input, Output, callback
from django_plotly_dash import DjangoDash
import copy


def plot_dashboard(data, user_accounts):
    df = pd.DataFrame(data)
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])

    app = DjangoDash('OPPS_Line', external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])
    lengths = {key: len(value) for key, value in data.items()}
    print("Lengths of data lists:", lengths)  # Check lengths of each column

    app.layout = html.Div(
        [
            html.Div([
                html.Div([
                    html.H5("Product", className='pt-4'),
                    dcc.Dropdown(
                        id="product",
                        options=[{"label": i, "value": i} for i in sorted(df["Product"].unique())],
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
                    html.H5("Advanced Plots", className='pt-4'),
                    dcc.Dropdown(
                        id="advanced-plots",
                        options=[
                            {"label": "Average Account Prices", "value": "account_prices"},
                            {"label": "Online Price Performance Score", "value": "OPPS"},
                            {"label": "Price Deviation Score", "value": "PDS"},
                            {"label": "Unit Sold", "value": "unit_sold"},
                            {"label": "Promo Depth", "value": "promo_depth"}
                        ],
                        value=None,
                        multi=False
                    ),
                    # Advanced Overlay Dropdown
                    html.H5("Advanced Overlay", className='pt-4', id='overlay-header'),
                    dcc.Dropdown(
                        id="advanced-overlay",
                        options=[
                            {"label": "Competitor", "value": "competitor"},
                            {"label": "Category", "value": "category"},
                            {"label": "Subcategory", "value": "subcategory"}
                        ],
                        value=None,
                        multi=True
                    ),
                ], className='card-body p-3'),
            ], className='container-fluid'),

            html.Div([
                html.Div([
                    html.H4("Online Price Performance Score Over Time (Grouped by 6-hour Intervals)", className='card-header pb-0'),
                    html.Div([
                        dcc.Graph(id="line"),
                    ]),
                ], className='card-body p-3'),
            ], className='container-fluid'),
        ], className='container-fluid'
    )

    # Callback to toggle the visibility of the advanced overlay dropdown
    @app.callback(
        Output('advanced-overlay', 'style'),
        Output('overlay-header', 'style'),
        Input('advanced-plots', 'value')
    )
    def toggle_advanced_overlay(advanced_plot):
        if advanced_plot in ["account_prices", "unit_sold"]:
            return {'display': 'block'}, {'display': 'block'}  # Show overlay dropdown and header
        return {'display': 'none'}, {'display': 'none'}  # Hide overlay dropdown and header

    # Existing callback to update the line chart remains unchanged
    @app.callback(
        Output("line", "figure"),
        Input("product", "value"),
        Input("period", "value"),
        Input("account", "value"),
        Input("advanced-plots", "value")
    )
    def update_line_chart(product, period, selected_accounts, advanced_plot):
        if selected_accounts is None:
            selected_accounts = []

        dff = copy.deepcopy(df)

        # Filter by selected product
        if product:
            dff = dff[dff["Product"] == product]

        # Set end and start dates for filtering
        end_date = dff['scraped_at'].max()
        if period == "last_week":
            start_date = end_date - pd.DateOffset(weeks=1)
        elif period == "last_month":
            start_date = end_date - pd.DateOffset(months=1)
        elif period == "last_6_months":
            start_date = end_date - pd.DateOffset(months=6)
        elif period == "last_year":
            start_date = end_date - pd.DateOffset(years=1)
        elif period == "ytd":
            start_date = pd.Timestamp(year=end_date.year, month=1, day=1, tz="UTC")
        else:
            start_date = dff['scraped_at'].min()

        dff = dff[(dff['scraped_at'] >= start_date) & (dff['scraped_at'] <= end_date)]

        dff['quarter_day'] = dff['scraped_at'].dt.floor('6h')
        price_columns = ['amazon_price', 'nahdi_price', 'dawa_price']
        dff[price_columns] = dff[price_columns].replace([None, 'N/A'], pd.NA).apply(pd.to_numeric, errors='coerce')
        # grouped_df = dff.groupby('quarter_day')[['amazon_price', 'nahdi_price', 'dawa_price', 'RSP_VAT']].mean().reset_index()
        grouped_df = dff.groupby('quarter_day')[['amazon_price', 'nahdi_price', 'dawa_price', 'RSP_VAT', 'opps']].mean().reset_index()

        fig = go.Figure()

        # Check if advanced plot is selected
        if advanced_plot is None:
            # Standard plot for each account's price
            for account in selected_accounts:
                if account == 'amazon' and 'amazon_price' in grouped_df.columns:
                    fig.add_trace(go.Scatter(
                        x=grouped_df['quarter_day'],
                        y=grouped_df['amazon_price'],
                        mode='lines',
                        name='Amazon Price'
                    ))
                elif account == 'nahdi' and 'nahdi_price' in grouped_df.columns:
                    fig.add_trace(go.Scatter(
                        x=grouped_df['quarter_day'],
                        y=grouped_df['nahdi_price'],
                        mode='lines',
                        name='Nahdi Price'
                    ))
                elif account == 'dawa' and 'dawa_price' in grouped_df.columns:
                    fig.add_trace(go.Scatter(
                        x=grouped_df['quarter_day'],
                        y=grouped_df['dawa_price'],
                        mode='lines',
                        name='Dawa Price'
                    ))
                # Optional RSP_VAT plot if data exists
                if 'RSP_VAT' in grouped_df.columns:
                    fig.add_trace(go.Scatter(
                        x=grouped_df['quarter_day'],
                        y=grouped_df['RSP_VAT'],
                        mode='lines',
                        name="RSP VAT",
                        line=dict(width=4, color='rgba(0, 255, 150, 0.8)', dash='dot'),
                        marker=dict(size=6),
                        opacity=0.9
                    ))

        elif advanced_plot == "account_prices":
            # Filter grouped_df to include only the selected account prices
            account_columns = []
            if 'amazon' in selected_accounts and 'amazon_price' in grouped_df.columns:
                account_columns.append('amazon_price')
            if 'nahdi' in selected_accounts and 'nahdi_price' in grouped_df.columns:
                account_columns.append('nahdi_price')
            if 'dawa' in selected_accounts and 'dawa_price' in grouped_df.columns:
                account_columns.append('dawa_price')

            # Calculate the average across the selected account columns
            if account_columns:
                grouped_df["average_price"] = grouped_df[account_columns].mean(axis=1)
                fig.add_trace(go.Scatter(
                    x=grouped_df['quarter_day'],
                    y=grouped_df["average_price"],
                    mode='lines',
                    name="Average Price",
                    line=dict(width=4, color='blue', dash='solid')
                ))


        elif advanced_plot == "OPPS":
            # Plot the OPPS values
            fig.add_trace(go.Scatter(
                x=grouped_df['quarter_day'],
                y=grouped_df['opps'],
                mode='lines',
                name='OPPS',
                line=dict(width=4, color='orange')
            ))

        

        fig.update_layout(
            xaxis_title="Scraped Date (6-hour Interval)",
            yaxis_title="Price",
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig

    return app
