1. How to Download a Dataset from the Platform {#1-download-dataset-platform}

Steps:

Step 1: Navigate to the top-left menu and select "Datasets".



Step 2: Search for your dataset using one of the following criteria:

Product name

Location

Dataset code (learn how to find a dataset code)

Dataset name



Step 3: Once you locate the dataset, click the "Visualize Record" button.



Step 4: Click the "Download" button at the top right of your screen.



Additional Note: The visualization interface displays comprehensive dataset information, including the dataset code, description, and other relevant metadata.

2. How to Download a TradeMatrix from the Platform {#2-download-tradematrix-platform}

Steps:

Step 1: Navigate to the top-left menu and select "TradeMatrix".



Step 2: Search for your TradeMatrix by name or code.



Step 3: Once you locate the TradeMatrix, click the "Visualize Record" button.



Step 4: Click the "Download" button at the top right of your screen.



3. How to Download a Dataset Using the Dnext API {#3-download-dataset-api}

Code Example:

Use the following Python code to download a dataset via the Dnext API:

import requests
import pandas as pd
from io import BytesIO
import time

def _get_task_status(task_id, token):
    my_headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
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

def download_dataset(code, token):
    my_headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    
    dl_url = f'https://api.dnext.io/v1.0/data/datasets/{code}/download'
    res = requests.post(dl_url, headers=my_headers)
    task_id = res.json()['task']['id']
    data_ready = _get_task_status(task_id, token)
    
    if data_ready:
        data_url = res.json()['result']['url']
        data_resp = requests.get(data_url)
        df = pd.read_csv(BytesIO(data_resp.content))
        df['Publication Date'] = pd.to_datetime(df['Publication Date'], errors='coerce')
        df_filtered = df[df['Publication Date'].dt.year >= 2025]
    else:
        df_filtered = None
    
    return df_filtered

# Usage
df = download_dataset(<dataset_code>, <your_token>)


Finding the Dataset Code:

You can locate the dataset code in two places:

Option 1: In the datasets list, under the "Code" column.



Option 2: On the dataset summary page.



4. How to Download a TradeMatrix Using the Dnext API {#4-download-tradematrix-api}

Code Example:

Use the following Python code to download a TradeMatrix via the Dnext API:

import requests
import pandas as pd
from io import BytesIO
import time
import json

def _get_task_status(task_id, token):
    my_headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
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

def download_tradeflow(code, token):
    my_headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    
    data = {
        'intraflows': {
            'strategy': 'include',  # "include" or "exclude" the intraflows
        },
        'forecasts': {
            'strategy': 'include',  # "include" or "exclude" the forecasts
            'list': ["forecast_code"]  # List of forecasts loaded in the TradeMatrix, ordered by priority
        },
        'row': True,
        'refresh': False,
        'format': 'csv',
    }
    
    dl_url = f'https://api.dnext.io/v1.0/fundamentals/tradeflows/{code}/download'
    res = requests.post(dl_url, headers=my_headers, data=json.dumps(data))
    task_id = res.json()['task']['id']
    data_ready = _get_task_status(task_id, token)
    
    if data_ready:
        data_url = res.json()['result']['url']
        data_resp = requests.get(data_url)
        df = pd.read_csv(BytesIO(data_resp.content))
    else:
        df = None
    
    return df

# Usage
df = download_tradeflow(<tradeflow_code>, <your_token>)


Finding the TradeMatrix Code:

Option 1: Extract it directly from the URL.



Option 2: Find it in the "Code" column of the TradeMatrix list.

Finding the Forecast Code:

Click the "Forecast" button in the top-right menu of the TradeMatrix.

Click "Load".



Copy the code shown in parentheses after the forecast name in the right panel where loaded forecasts are displayed.



5. How to Find a Dataset Code {#5-find-dataset-code}

Steps:

Step 1: Click the "Datasets" button at the top left of the platform.



Step 2: Search for your dataset by name, product, location, or other criteria.



Step 3: Once you locate your dataset, you have two options:

Option 1: View the dataset code directly in the list.



Option 2: Click the "Visualize" button.



Then view the dataset code on the summary interface.



6. Login Authentication Failure {#6-login-authentication-failure}

Summary

Users are unable to access the platform due to incorrect or expired login credentials.

Symptoms

Unable to log in

Authentication error messages

Password expired notifications

Causes

Incorrect username or password

Expired credentials

System authentication changes

Prerequisites

Access to the platform URL

Knowledge of account credentials

Resolution Steps

Verify the platform URL is correct.

Confirm that the username and password match the provided credentials.

If credentials are expired or have been changed, reset the password using the platform's recovery option.

If the issue persists, contact support and provide error details.

Verification Steps

Attempt to log in using updated credentials.

Check for any system notifications regarding authentication changes.

Additional Notes

Ensure credentials are valid and have not been altered by the user.

Check for recent authentication system updates if the problem continues.

Related Articles

Password Reset, Expired Credentials

7. Password Reset Required {#7-password-reset-required}

Summary

Users are required to reset their password after initial login.

Symptoms

Prompt to change password immediately after login.

Causes

New account creation

System policy requiring password change on first login

Prerequisites

Successful login with temporary credentials

Resolution Steps

Follow on-screen instructions to change your password upon login.

Create a strong, unique password following platform guidelines.

Confirm the new password by re-entering it.

Verification Steps

Log out and log back in using the new password.

Additional Notes

Ensure the password meets complexity requirements to prevent future login issues.

Related Articles

Password Best Practices

8. Expired Credentials {#8-expired-credentials}

Summary

Users cannot log in due to expired credentials.

Symptoms

Login failure indicating expired credentials.

Causes

Password expiration reached

Credentials revoked

Prerequisites

Access to the platform's credential recovery system

Resolution Steps

Use the password recovery option to reset credentials.

Enter the verification code sent from no-reply@dnext.io.

Follow the provided steps to complete the reset.

If self-service reset fails, contact support.

Verification Steps

Attempt to log in with new credentials.

Additional Notes

Review the account expiration policy to prevent recurrence.

Related Articles

Password Reset

9. Visualization Issues {#9-visualization-issues}

Dashboard Data Not Displaying

Summary

Data is missing due to filters, source issues, or configuration errors.

Symptoms

Empty charts

Missing data rows

Causes

Incorrect filter settings

Connectivity issues

Misconfiguration

Data validation errors

Prerequisites

Access to dashboard

Knowledge of data source

Resolution Steps

Verify filter settings are correct.

Try changing filter values, as some combinations may not have available data.

Clear browser cache if issues persist.

Verification Steps

Try different filter values and combinations. If all attempts fail, contact support.

Additional Notes

Clear browser cache to resolve potential display issues.

10. How to Navigate Dashboards {#10-navigate-dashboards}

(Content to be added)

11. How to Download Data from a Dashboard {#11-download-dashboard-data}

(Content to be added)

❓ Frequently Asked Questions (FAQs)

Q1: What should I do if I forget my password?

Use the "Forgot Password" option. A verification code will be sent to your email address from no-reply@dnext.io. Enter the code and follow the instructions to reset your password.

Q2: What if I can't access the platform even with correct credentials?

Verify the platform URL is correct. If the URL is correct and you still cannot access the platform, contact support with the error details.

🔧 Troubleshooting Guide

Diagnostic Steps

Verify the platform URL and authentication system status.

Confirm credentials match the provided ones.

Test with a different device or browser.

If using a VPN, try disabling it as some VPNs block authentication requests.

Common Fixes

Reset password

Clear browser cache and cookies

Disable VPN

Escalation Criteria

If self-service fixes fail, escalate to support with error details and timestamps.

Logs to Capture

Login attempt logs

Authentication error messages

✅ Best Practices

Use strong, unique passwords and change them regularly.

Keep recovery contact information current.

If using a VPN, ensure it is not blocking the platform. If it is, contact your IT department to whitelist it.

Report unauthorized credential changes immediately.

Keep data filters updated for accurate reporting.