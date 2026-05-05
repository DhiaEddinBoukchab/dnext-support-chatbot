import requests
import pandas as pd
from io import BytesIO
import time
import json
import os
from pathlib import Path


# ==========================
# 🔐 AUTH
# ==========================
def connect(email, password, env):
    print("🔐 Connecting to API...")

    url = f"https://api.dnext.io/v1.0/auth/custom-login?org={env}"

    payload = {
        "email": email,
        "password": password,
        "organization": env
    }

    response = requests.post(url, json=payload, timeout=30)

    if response.status_code == 200:
        print("✅ Connected!")
        return response.json().get("token")
    else:
        print("❌ Login error:", response.text)
        raise Exception("Authentication failed")


# ==========================
# ⏳ WAIT FOR TASK
# ==========================
def wait_for_task(task_id, token, code):
    """
    Polls until the task is SUCCEEDED.
    The URL comes from the POST response — this just waits for the file to be ready.
    """
    headers = {"Authorization": f"Bearer {token}"}

    for attempt in range(30):
        time.sleep(2)

        r = requests.get(
            f"https://api.dnext.io/v1.0/tasks/{task_id}",
            headers=headers,
            timeout=30
        )

        try:
            data = r.json()
        except Exception:
            print(f"❌ Invalid JSON for {code} (attempt {attempt+1})")
            continue

        status = data.get("status")
        print(f"⏳ Task status for {code}: {status} (attempt {attempt+1})")

        if status == "SUCCEEDED":
            return True

        if status in ["FAILED", "CANCELLED"]:
            print(f"❌ Task failed for {code}: {status}")
            return False

    print(f"⏱️ Timeout for {code} after 30 attempts")
    return False


# ==========================
# 📥 DOWNLOAD ONE TRADEFLOW
# ==========================
def download_tradeflow(code, token, config):
    headers = {"Authorization": f"Bearer {token}"}

    if config.get("include"):
        forecasts = {
            "strategy": "include",
            "list": [config["forecast_code"]]
        }
    else:
        forecasts = {
            "strategy": "exclude",
            "list": []
        }

    payload = {
        "intraflows": {"strategy": "include"},
        "forecasts": forecasts,
        "row": True,
        "refresh": False,
        "format": "csv",
    }

    url = f"https://api.dnext.io/v1.0/fundamentals/tradeflows/{code}/download"

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)

        try:
            res_json = res.json()
        except Exception:
            print(f"❌ Invalid response for {code}: {res.text}")
            return None

        # ✅ URL comes directly from the POST response
        data_url = res_json.get("result", {}).get("url")

        if not data_url:
            print(f"❌ No URL in POST response for {code}")
            return None

        # ⏳ Wait for task to complete before downloading
        task = res_json.get("task", {})
        task_id = task.get("id")
        task_status = task.get("status", "").upper()

        if task_id and task_status not in ("SUCCEEDED",):
            print(f"📋 Task {task_id} in progress, waiting...")
            success = wait_for_task(task_id, token, code)
            if not success:
                return None

        # ⬇️ Download the CSV
        print(f"⬇️ Fetching CSV for {code}...")
        data_resp = requests.get(data_url, timeout=60)

        df = pd.read_csv(BytesIO(data_resp.content))
        df["tradeflow_code"] = code

        return df

    except Exception as e:
        print(f"❌ Error {code}: {e}")
        return None


# ==========================
# 📦 MULTI TRADEFLOW
# ==========================
def download_multiple_tradeflows(configs, token, merge=True, output_dir=None):
    results = {}

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Output folder: {output_dir}")

    for code, config in configs.items():
        print(f"\n{'='*60}")
        print(f"⬇️ Downloading {code} ...")
        print(f"{'='*60}")

        df = download_tradeflow(code, token, config)

        if df is not None:
            results[code] = df
            print(f"✅ Success {code} — {len(df)} rows")

            # 💾 Save individual CSV
            if output_dir:
                file_path = os.path.join(output_dir, f"{code}.csv")
                df.to_csv(file_path, index=False)
                print(f"💾 Saved: {file_path}")
        else:
            print(f"⚠️ Failed {code}")

        time.sleep(1)

    if merge and results:
        merged = pd.concat(results.values(), ignore_index=True)

        # 💾 Save merged CSV
        if output_dir:
            merged_path = os.path.join(output_dir, "ALL_TRADEFLOWS_MERGED.csv")
            merged.to_csv(merged_path, index=False)
            print(f"\n💾 Merged file saved: {merged_path}")
            print(f"📊 Total rows in merged file: {len(merged)}")

        return merged

    return results


# ==========================
# 🔧 USER CONFIG
# ==========================
def get_user_config():
    """
    Centralized place to configure credentials and output folder.
    Change ONLY this section for different users.
    """
    return {
        # 🔐 Credentials
        "email": "your_email",   # ← change per user
        "password": "your_password",              # ← change per user
        "env": "drw",                          # ← change per user/environment

        # 📁 Output folder (auto-created if it doesn't exist)
        # Uses the current user's Downloads folder automatically
        "output_dir": os.path.join(Path.home(), "Downloads", "tradeflows"),

        # 🎯 Tradeflows to download
        "tradeflows": {
            "drw-6ec88e56-dd88-4fb4-8eee-6b0e93145106": {
                "include": False
            },
            "drw-ca8d27e7-95d7-4ffa-a34e-e45f7ede933f": {
                "include": True,
                "forecast_code": "drw-833b0793-c3b0-454d-b4b9-4038f4acdc18"
            },
            "drw-cb0a7685-b38d-4c8d-9700-c8547c701165": {
                "include": False
            },
            "drw-3fe60612-e85d-4da8-92a8-e188a352a49b": {
                "include": False
            },
            "drw-286a5661-62a5-43d0-8136-d737187c3779": {
                "include": False
            },
            "drw-5fe8a6f5-9c4e-4c5e-ab45-4faeabcf7c11": {
                "include": False
            },
        }
    }


# ==========================
# 🚀 MAIN
# ==========================
if __name__ == "__main__":

    # Load config
    config = get_user_config()

    # Connect
    token = connect(
        email=config["email"],
        password=config["password"],  # Note: connect() uses "pwd" parameter
        env=config["env"]
    )

    # Download all tradeflows
    df = download_multiple_tradeflows(
        configs=config["tradeflows"],
        token=token,
        merge=True,
        output_dir=config["output_dir"]
    )

    # Preview
    if isinstance(df, pd.DataFrame):
        print("\n📊 Preview:")
        print(df.head())
        print(f"\nTotal rows: {len(df)}")
    else:
        print("❌ No data retrieved")