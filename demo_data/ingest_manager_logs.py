import requests
import pandas as pd
import re
import urllib3
urllib3.disable_warnings()

# ── Read HEC token from .env ──────────────────────────
env_content  = open('.env').read()
token_match  = re.search(r'SPLUNK_HEC_TOKEN=(.+)', env_content)
TOKEN        = token_match.group(1).strip() if token_match else ""

HEC_URL = "https://localhost:8088/services/collector/event"
HEADERS = {
    "Authorization": f"Splunk {TOKEN}",
    "Content-Type":  "application/json"
}

# ── Read manager's CSV file ───────────────────────────
CSV_PATH = "demo_data/scores_sample_logs.csv"

# ── Flag → Level mapping ──────────────────────────────
LEVEL_MAP = {
    'IAC25M':  'INFO',
    'restart': 'ERROR',
    'RCE':     'ERROR',
    'RB':      'WARN',
    'PRCPORT': 'ERROR',
    'ports':   'ERROR',
    'nscan':   'ERROR',
    'upt':     'WARN',
    'amt':     'WARN',
}

# ── Flag → Human readable message ────────────────────
MSG_MAP = {
    'IAC25M':  'Exam score submitted successfully',
    'restart': 'Machine restarted during live exam — possible tampering',
    'RCE':     'Remote code execution attempt detected on exam machine',
    'RB':      'Reboot detected during active exam session',
    'PRCPORT': 'Port scan detected — possible network intrusion',
    'ports':   'Unauthorized port activity on exam machine',
    'nscan':   'Network scan from exam machine detected',
    'upt':     'Uptime anomaly — machine may have been restarted',
    'amt':     'Intel AMT management interface active — security risk',
}

def parse_event(event_str):
    """Parse key=value pairs from event.original field."""
    result = {}
    pairs = re.findall(r'(\w+)=([^\s,]+)', str(event_str))
    for k, v in pairs:
        result[k] = v
    return result

def send():
    if not TOKEN:
        print("ERROR: SPLUNK_HEC_TOKEN not found in .env")
        return

    print(f"Token: {TOKEN[:8]}...")

    # ── Load CSV ──────────────────────────────────────
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"CSV loaded: {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
    except FileNotFoundError:
        print(f"ERROR: File not found at {CSV_PATH}")
        print("Copy your manager's CSV file to:")
        print(f"  ~/agentic_splunk_ai/{CSV_PATH}")
        return

    print(f"\nSending {len(df)} exam log events to Splunk...\n")

    success = 0
    failed  = 0
    counts  = {"INFO":0,"ERROR":0,"WARN":0}

    for i, row in df.iterrows():

        # ── Parse the event.original field ───────────
        parsed = parse_event(row.get('event.original',''))
        flag   = parsed.get('flag', 'unknown')
        level  = LEVEL_MAP.get(flag, 'INFO')
        msg    = MSG_MAP.get(flag, f"Exam event: flag={flag}")

        # ── Build clean structured log event ─────────
        log_event = {
            # Core fields
            "service":    f"exam-center-{parsed.get('centercode','unknown')}",
            "level":      level,
            "message":    msg,

            # Exam specific fields
            "flag":       flag,
            "score":      parsed.get('score', ''),
            "centercode": parsed.get('centercode', ''),
            "macid":      parsed.get('macid', ''),
            "ip":         parsed.get('ip', ''),
            "timestamp":  parsed.get('event_date', ''),

            # Server fields from CSV columns
            "pxesrv_id":  str(row.get('fields.pxesrv_id', '')),
            "exam_mode":  str(row.get('fields.exam_mode', 'live')),
            "ccode":      str(row.get('fields.ccode', '')),
            "log_file":   str(row.get('log.file.path', '')),
        }

        # ── HEC payload ───────────────────────────────
        payload = {
            "event":      log_event,
            "source":     "exam_logs",
            "sourcetype": "exam_monitoring",
            "index":      "main"
        }

        # ── Send to Splunk ────────────────────────────
        try:
            resp = requests.post(
                HEC_URL,
                headers=HEADERS,
                json=payload,
                verify=False,
                timeout=5
            )
            if resp.status_code == 200:
                success += 1
                counts[level] += 1
                # Print only first 5 and all errors
                if i < 5 or level in ('ERROR','WARN'):
                    icon = "✅" if level=="INFO" else \
                           "⚠️" if level=="WARN" else "❌"
                    print(f"{icon} [{level}] center={parsed.get('centercode','')} "
                          f"flag={flag} score={parsed.get('score','')} "
                          f"ip={parsed.get('ip','')}")
            else:
                failed += 1
                print(f"❌ HTTP {resp.status_code}: {resp.text[:60]}")

        except Exception as e:
            failed += 1
            if failed <= 3:
                print(f"❌ Error: {str(e)[:80]}")

    # ── Final summary ─────────────────────────────────
    print(f"\n{'='*60}")
    print(f"✅ Sent:    {success}")
    print(f"❌ Failed:  {failed}")
    print(f"\nBreakdown:")
    print(f"  INFO  (normal):   {counts['INFO']}")
    print(f"  WARN  (suspect):  {counts['WARN']}")
    print(f"  ERROR (critical): {counts['ERROR']}")

    if success > 0:
        print(f"\n{'='*60}")
        print("Now search in Splunk:")
        print()
        print("1. All exam logs:")
        print("   index=main source=exam_logs | head 20")
        print()
        print("2. All problems:")
        print("   index=main source=exam_logs level=ERROR")
        print("   | stats count by message | sort -count")
        print()
        print("3. Worst centers:")
        print("   index=main source=exam_logs level=ERROR")
        print("   | stats count by centercode | sort -count")
        print()
        print("4. RCE attacks:")
        print("   index=main source=exam_logs flag=RCE")
        print("   | table _time centercode macid ip score")

if __name__ == "__main__":
    send()
