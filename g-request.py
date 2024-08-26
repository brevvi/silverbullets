import os
import json
import csv
import pandas as pd
import plotly.express as px
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.oauth2 import service_account
from flask import Flask, render_template_string

app = Flask(__name__)

def fetch_and_save_data():
    # Load the service account credentials from the JSON file directly
    with open('ga4-signals-433619-954e21272616.json') as json_file:
        credentials_info = json.load(json_file)

    # Use the credentials to create a BetaAnalyticsDataClient
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    client = BetaAnalyticsDataClient(credentials=credentials)

    # Define the request to Google Analytics API
    request = {
        "property": f"properties/254400201",  # Replace with your actual property ID
        "dateRanges": [{"startDate": "2023-08-17", "endDate": "2023-08-23"}],
        "dimensions": [{"name": "date"}],
        "metrics": [{"name": "sessions"}, {"name": "totalUsers"}, {"name": "screenPageViews"},
                    {"name": "conversions"}, {"name": "eventCount"}, {"name": "userEngagementDuration"}]
    }

    # Fetch the data from Google Analytics
    response = client.run_report(request)

    # Prepare the data for CSV export
    rows = []
    for row in response.rows:
        rows.append([dim_value.value for dim_value in row.dimension_values] +
                    [metric_value.value for metric_value in row.metric_values])

    # Write the data to a CSV file
    with open('analytics_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Sessions", "Total Users", "Screen Pageviews", "Conversions", "Event Count", "User Engagement Duration"])
        writer.writerows(rows)

@app.route('/')
def index():
    # First, fetch and save the latest data
    fetch_and_save_data()

    # Read the processed data from the CSV
    df = pd.read_csv('analytics_data.csv')

    # Create plots using Plotly
    fig1 = px.line(df, x='Date', y='Sessions', title='Sessions Over Time')
    fig2 = px.line(df, x='Date', y='Total Users', title='Total Users Over Time')
    fig3 = px.line(df, x='Date', y='Screen Pageviews', title='Screen Pageviews Over Time')
    fig4 = px.line(df, x='Date', y='Conversions', title='Conversions Over Time')
    fig5 = px.line(df, x='Date', y='Event Count', title='Event Count Over Time')
    fig6 = px.line(df, x='Date', y='User Engagement Duration', title='User Engagement Duration Over Time')

    # Convert plots to HTML
    fig1_html = fig1.to_html(full_html=False)
    fig2_html = fig2.to_html(full_html=False)
    fig3_html = fig3.to_html(full_html=False)
    fig4_html = fig4.to_html(full_html=False)
    fig5_html = fig5.to_html(full_html=False)
    fig6_html = fig6.to_html(full_html=False)

    # Since index.html is not in the templates folder, we use render_template_string
    with open('index.html', 'r') as file:
        template = file.read()
    
    # Render the HTML template with the plots
    return render_template_string(template, fig1_html=fig1_html, fig2_html=fig2_html, 
                                  fig3_html=fig3_html, fig4_html=fig4_html, fig5_html=fig5_html, fig6_html=fig6_html)

if __name__ == '__main__':
    app.run(debug=True)
