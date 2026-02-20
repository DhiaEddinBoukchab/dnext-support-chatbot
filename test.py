import requests
import pandas as pd
from io import BytesIO
import time
import json

# Step 1: Authenticate and get token
def connect(email, pwd, env):
    url = f'https://api.dnext.io/v1.0/auth/custom-login?org={env}'
    payload = json.dumps({
        'email': email,
        'password': pwd,
        'organization': env
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)
    token = response.json()['token']
    return token

# Step 2: Poll task status
def _get_task_status(task_id, token):
    my_headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    success = False
    wait_time = 2
    while not success and wait_time < 30:
        time.sleep(wait_time)
        status_res = requests.get(f'https://api.dnext.io/v1.0/tasks/{task_id}', headers=my_headers)
        try:
            success = status_res.json()['status'] == 'SUCCEEDED'
        except:
            wait_time += 1
            continue
        if not success:
            wait_time += 1
    return success

# Step 3: Download tradeflow data
def download_tradeflow(code, token):
    my_headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    data = {
        "intraflows": {"strategy": "exclude"},
        "forecasts": {"strategy": "exclude"},
        "row": False,
        "format": "csv"
    }
    dl_url = f'https://api.dnext.io/v1.0/fundamentals/tradeflows/{code}/download'
    res = requests.post(dl_url, headers=my_headers, data=json.dumps(data))
    # Check for error in response
    if 'task' not in res.json():
        print("Error:", res.json())
        return None
    task_id = res.json()['task']['id']
    data_ready = _get_task_status(task_id, token)
    if data_ready:
        data_url = res.json()['result']['url']
        data_resp = requests.get(data_url)
        df = pd.read_csv(BytesIO(data_resp.content))
        return df
    else:
        print("Data not ready")
        return None

# Usage example
email = "ce-data-notifications@drwuk.com"
password = "YOUR_PASSWORD"
env = "YOUR_ENV"  # e.g., 'drw'
tradeflow_code = "drw-ca8d27e7-95d7-4ffa-a34e-e45f7ede933f"

token = connect(email, password, env)
df = download_tradeflow(tradeflow_code, token)
if df is not None:
    print(df.head())