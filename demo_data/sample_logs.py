import json
import datetime

DEMO_LOGS = [
    {"service":"payment-service","level":"INFO", "message":"Transaction processed successfully","response_time":120},
    {"service":"payment-service","level":"INFO", "message":"Payment gateway connected","response_time":98},
    {"service":"auth-service",   "level":"INFO", "message":"User login successful","response_time":45},
    {"service":"api-gateway",    "level":"INFO", "message":"Request routed successfully","response_time":23},
    {"service":"payment-service","level":"WARN", "message":"DB connection pool at 70% capacity","response_time":450},
    {"service":"payment-service","level":"WARN", "message":"Response time degrading","response_time":890},
    {"service":"database",       "level":"WARN", "message":"Connection wait time increasing","response_time":1200},
    {"service":"payment-service","level":"ERROR","message":"DB connection pool exhausted","response_time":9999},
    {"service":"payment-service","level":"ERROR","message":"Connection timeout after 30000ms","response_time":30000},
    {"service":"api-gateway",    "level":"ERROR","message":"Upstream payment-service timeout","response_time":30000},
    {"service":"order-service",  "level":"ERROR","message":"Payment validation failed","response_time":15000},
    {"service":"database",       "level":"ERROR","message":"Max connections reached 500/500","response_time":99999},
    {"service":"database",       "level":"ERROR","message":"Memory usage critical 94%","response_time":99999},
]

def generate():
    now  = datetime.datetime.now(datetime.UTC)
    logs = []
    for i, log in enumerate(DEMO_LOGS):
        entry = log.copy()
        entry["timestamp"] = (now - datetime.timedelta(minutes=len(DEMO_LOGS)-i)).isoformat()
        entry["host"]      = "prod-server-01"
        logs.append(entry)
    return logs

if __name__ == "__main__":
    logs = generate()
    print(json.dumps(logs, indent=2))
    print(f"\nGenerated {len(logs)} log events")
