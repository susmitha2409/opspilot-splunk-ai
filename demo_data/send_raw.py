import requests
import urllib3
import re
urllib3.disable_warnings()

# Get token
env     = open('.env').read()
match   = re.search(r'SPLUNK_HEC_TOKEN=(.+)', env)
TOKEN   = match.group(1).strip() if match else ""

HEC_URL = "https://localhost:8088/services/collector/event"
HEADERS = {
    "Authorization": f"Splunk {TOKEN}",
    "Content-Type":  "application/json"
}

# Read raw CSV and send EXACTLY as is
with open('scores_sample_logs.csv','r') as f:
    lines = f.readlines()

headers = lines[0].strip().split(',')
print(f"Sending {len(lines)-1} raw log lines to Splunk...")

success = 0
failed  = 0

for i, line in enumerate(lines[1:], 1):
    # Send completely raw — zero modification
    payload = {
        "event":  line.strip(),
        "source": "raw_exam_logs",
        "index":  "main"
    }
    try:
        resp = requests.post(
            HEC_URL, headers=HEADERS,
            json=payload, verify=False, timeout=5
        )
        if resp.status_code == 200:
            success += 1
            if i <= 3:
                print(f"✅ Sent raw line {i}: {line[:80]}...")
        else:
            failed += 1
            if failed <= 2:
                print(f"❌ {resp.status_code}: {resp.text}")
    except Exception as e:
        failed += 1
        if failed <= 2:
            print(f"❌ {e}")

print(f"\n✅ Sent: {success}   ❌ Failed: {failed}")
print("\nSearch in Splunk:")
print("  index=main source=raw_exam_logs | head 20")
