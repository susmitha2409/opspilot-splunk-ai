import requests
import json
import datetime
import re
import urllib3
urllib3.disable_warnings()

# Read token from .env
env_content = open('.env').read()
token_match  = re.search(r'SPLUNK_HEC_TOKEN=(.+)', env_content)
TOKEN = token_match.group(1).strip() if token_match else ""

# Try HTTPS first, fallback to HTTP
URLS_TO_TRY = [
    "https://localhost:8088/services/collector/event",
    "http://localhost:8088/services/collector/event",
]

HEADERS = {
    "Authorization": f"Splunk {TOKEN}",
    "Content-Type":  "application/json"
}

DEMO_LOGS = [
    {"service":"payment-service","level":"INFO", "message":"Transaction processed successfully",         "response_time":120},
    {"service":"payment-service","level":"INFO", "message":"Payment gateway connected",                  "response_time":98},
    {"service":"auth-service",   "level":"INFO", "message":"User login successful",                     "response_time":45},
    {"service":"api-gateway",    "level":"INFO", "message":"Request routed successfully",                "response_time":23},
    {"service":"database",       "level":"INFO", "message":"DB connection pool healthy 45/500",          "response_time":5},
    {"service":"payment-service","level":"WARN", "message":"DB connection pool at 70% capacity",        "response_time":450},
    {"service":"payment-service","level":"WARN", "message":"Response time degrading 890ms",             "response_time":890},
    {"service":"database",       "level":"WARN", "message":"Connection wait time increasing 1200ms",    "response_time":1200},
    {"service":"database",       "level":"WARN", "message":"Memory usage at 78%",                       "response_time":0},
    {"service":"payment-service","level":"ERROR","message":"DB connection pool exhausted 500/500",       "response_time":9999},
    {"service":"payment-service","level":"ERROR","message":"Connection timeout after 30000ms",           "response_time":30000},
    {"service":"payment-service","level":"ERROR","message":"Failed to process transaction no DB connections","response_time":30000},
    {"service":"api-gateway",    "level":"ERROR","message":"Upstream payment-service timeout",           "response_time":30000},
    {"service":"order-service",  "level":"ERROR","message":"Payment validation failed service unavailable","response_time":15000},
    {"service":"auth-service",   "level":"ERROR","message":"JWT validation service timeout 8000ms",      "response_time":8000},
    {"service":"database",       "level":"ERROR","message":"Max connections reached 500/500",            "response_time":99999},
    {"service":"database",       "level":"ERROR","message":"Memory usage critical 94%",                  "response_time":99999},
    {"service":"database",       "level":"ERROR","message":"OOM killer activated",                       "response_time":99999},
]

def find_working_url():
    """Test which URL works."""
    print("Testing HEC connection...")
    for url in URLS_TO_TRY:
        try:
            resp = requests.get(
                url.replace("/services/collector/event", "/services/collector/health"),
                headers=HEADERS,
                verify=False,
                timeout=5
            )
            print(f"  ✅ Working URL: {url}")
            return url
        except Exception as e:
            print(f"  ❌ {url} → {str(e)[:50]}")
    return None

def send():
    if not TOKEN:
        print("ERROR: SPLUNK_HEC_TOKEN not set in .env")
        return

    print(f"Token: {TOKEN[:8]}...\n")

    # Find working URL
    working_url = find_working_url()
    if not working_url:
        print("\nCannot reach Splunk HEC on port 8088.")
        print("Fix: Enable HEC in Splunk Web UI:")
        print("  Settings → Data Inputs → HTTP Event Collector")
        print("  Global Settings → Enable ALL tokens → Save")
        return

    print(f"\nSending {len(DEMO_LOGS)} logs...\n")

    now     = datetime.datetime.now(datetime.UTC)
    success = 0
    failed  = 0

    for i, log in enumerate(DEMO_LOGS):
        log_copy  = log.copy()
        timestamp = now - datetime.timedelta(minutes=len(DEMO_LOGS)-i)
        log_copy["timestamp"] = timestamp.isoformat()
        log_copy["host"]      = "prod-server-01"
        log_copy["env"]       = "production"

        payload = {
            "event":      log_copy,
            "source":     "demo_app",
            "sourcetype": "json",
            "index":      "main",
            "time":       timestamp.timestamp()
        }

        try:
            resp = requests.post(
                working_url,
                headers=HEADERS,
                json=payload,
                verify=False,
                timeout=5
            )
            if resp.status_code == 200:
                success += 1
                icon = "✅" if log["level"]=="INFO" else "⚠️" if log["level"]=="WARN" else "❌"
                print(f"{icon} [{log['level']}] {log['service']}: {log['message'][:55]}")
            else:
                failed += 1
                print(f"❌ HTTP {resp.status_code}: {resp.text[:80]}")
        except Exception as e:
            failed += 1
            print(f"❌ Error: {str(e)[:80]}")

    print(f"\n{'='*55}")
    print(f"✅ Sent: {success}   ❌ Failed: {failed}")

    if success > 0:
        print("\nVerify in Splunk Search & Reporting:")
        print("  index=main | head 20")
        print("  index=main level=ERROR | stats count by service")

if __name__ == "__main__":
    send()
