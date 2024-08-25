import os
import json  # Adicionando a importação do módulo json
from flask import Flask, render_template, jsonify
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

app = Flask(__name__)


def fetch_and_save_data():
    # Verifica se a variável de ambiente está definida
    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not service_account_info:
        raise ValueError("A variável de ambiente GOOGLE_SERVICE_ACCOUNT_JSON não está definida.")

    # Converte a string JSON para um dicionário
    service_account_info = json.loads(service_account_info)

    # Cria o cliente do Google Analytics Data API
    client = BetaAnalyticsDataClient.from_service_account_info(service_account_info)

    # Definindo o ID da propriedade do Google Analytics
    property_id = "254400201"

    # Define a requisição para o relatório
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="conversions"),
            Metric(name="eventCount"),
            Metric(name="userEngagementDuration")
        ],
        date_ranges=[DateRange(start_date="2023-01-01", end_date="2023-12-31")],
    )

    # Executa a requisição do relatório
    response = client.run_report(request)

    # Prepara os dados para exibição no HTML
    data = {
        "sessions": [],
        "totalUsers": [],
        "screenPageViews": [],
        "conversions": [],
        "eventCount": [],
        "userEngagementDuration": [],
        "dates": []
    }

    for row in response.rows:
        data["dates"].append(row.dimension_values[0].value)
        data["sessions"].append(int(row.metric_values[0].value))
        data["totalUsers"].append(int(row.metric_values[1].value))
        data["screenPageViews"].append(int(row.metric_values[2].value))
        data["conversions"].append(int(row.metric_values[3].value))
        data["eventCount"].append(int(row.metric_values[4].value))
        data["userEngagementDuration"].append(int(row.metric_values[5].value))

    return data


@app.route('/')
def index():
    try:
        data = fetch_and_save_data()
        return render_template('index.html', data=data)
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
