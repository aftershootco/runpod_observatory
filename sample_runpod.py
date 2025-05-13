# coding: utf-8
import runpod
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta
from requests import post
import pandas as pd

op = os.path
SUMMARY_COLS = ['gpu_util', 'gpu_mem']
SUMMARY_COLNAMES = ['GPU Use (%)', 'GPU Memory (%)']
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
SUMMARY_TMPL = """*In the last 24 hours,*

  🟢 *%d GPU instances* ran for a total of nearly *%d hours*

  💸 We spent approx *$%d*

  📈 The *most active instance* had an average GPU utilization of *%d%%*

  📊 The *average GPU utilization was %d%%*
"""


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


def daily_summary(client):
    spreadsheet = client.open_by_key("1_X8YlG4UBTVJfAIuknew64BZECCcBWrjoA_FibLYmDQ")
    worksheet = spreadsheet.worksheet("Sheet1")
    df = pd.DataFrame(worksheet.get_all_records())
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    since = datetime.now(timezone.utc) - timedelta(days=1)
    df = df[df['timestamp'] >= since]
    df = df[df['gpuCount'] > 0]
    running = df[df['desiredStatus'] == 'RUNNING']
    summary_df = (
        running.groupby('name')[SUMMARY_COLS].mean().sort_values('gpu_util', ascending=False)
    )
    summary_df.columns = SUMMARY_COLNAMES
    slack_blocks = [
        "*RunPod Summary*",
        SUMMARY_TMPL
        % (
            len(summary_df),
            len(running),
            int(running['costPerHr'].sum()),
            int(summary_df.iloc[0]['GPU Use (%)']),
            int(summary_df['GPU Use (%)'].mean()),
        ),
        f"```{summary_df.to_markdown()}```",
    ]
    return slack_blocks, summary_df


if __name__ == "__main__":
    client = auth()
    webhook = os.environ.get('SLACK_WEBHOOK', False)
    if webhook:
        blocks, df = daily_summary(client)
        blocks = [{'type': 'section', 'text': {'type': 'mrkdwn', 'text': b}} for b in blocks]
        response = post(
            webhook,
            headers={'Content-Type': 'application/json'},
            json={"blocks": blocks},
            timeout=30,
        )
        print(response.text)  # noqa
        response.raise_for_status()
    else:
        sample(client)
