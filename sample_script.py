# coding: utf-8
import runpod
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

op = os.path

QUERY = """query Pod {
  pod(input: {podId: "%s"}) {
    id
    name
    latestTelemetry {
      cpuUtilization
      memoryUtilization
      averageGpuMetrics {
        percentUtilization
        memoryUtilization
      }
    }
  }
}"""


def auth():
    key = os.environ['GCS_SA']
    if op.isfile(key):
        with open(key) as f:
            creds = json.load(f)
    else:
        creds = json.loads(key)
    creds = Credentials.from_service_account_info(
        creds, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds)


def get_telemetry(pod_id):
    query = QUERY % pod_id
    result = runpod.api.graphql.run_graphql_query(query)
    latest_telemetry = result['data']['pod']['latestTelemetry']
    cpu_util = latest_telemetry['cpuUtilization']
    mem_util = latest_telemetry['memoryUtilization']
    gpu_metrics = latest_telemetry['averageGpuMetrics']
    return [
        cpu_util,
        mem_util,
        gpu_metrics['percentUtilization'],
        gpu_metrics['memoryUtilization'],
    ]


def sample(client):
    spreadsheet = client.open_by_key("1_X8YlG4UBTVJfAIuknew64BZECCcBWrjoA_FibLYmDQ")  # from URL
    worksheet = spreadsheet.worksheet("Sheet1")  # or by title
    runpod.api_key = os.environ['RUNPOD_KEY']
    pods = runpod.get_pods()
    payload = []
    for pod in pods:
        del pod['runtime']
        del pod['env']
        del pod['machine']
        pod['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload.append(list(pod.values()) + get_telemetry(pod['id']))
    worksheet.append_rows(payload, value_input_option="USER_ENTERED", table_range="A1")


if __name__ == "__main__":
    client = auth()
    sample(client)
