# OpsPilot AI — Architecture Diagram

## 1. How the Application Interacts with Splunk

```
Application Logs / Microservices / Kubernetes Pods
                    │
                    │  HTTP Event Collector (HEC) — Port 8088
                    ▼
        ┌────────────────────────────┐
        │      SPLUNK ENTERPRISE      │
        │   REST API : Port 8089      │
        │   HEC      : Port 8088      │
        │   Web UI   : Port 8000      │
        └─────────────┬──────────────┘
                       │
       ┌───────────────┴───────────────┐
       │  READ (REST API)               │  WRITE (HEC)
       │  QueryAgent runs SPL search    │  Orchestrator sends AI
       │  to fetch telemetry            │  intelligence report back
       ▼                                 ▼
```

OpsPilot AI integrates with Splunk bidirectionally:

- **Reading** — The Query Agent issues SPL searches via Splunk's REST API (`/services/search/jobs`) to pull recent logs for the service under investigation.
- **Writing** — After every investigation, the full AI report is sent back into Splunk via HTTP Event Collector, indexed under `source=ai_ops_intelligence`, making it searchable in Splunk dashboards alongside the original logs.

---

## 2. How AI Models / Agents Are Integrated

```
                  MCP SERVER
   (Tool Registry — search_splunk, get_error_logs,
    get_k8s_pod_status, trigger_investigation)
                      │
                      ▼
            AGENT ORCHESTRATOR
   (Python asyncio.gather — parallel execution)
   ┌─────────┬─────────┬──────────┬─────────────┐
   │  Query  │   RCA   │   Risk   │ Correlation │
   │  Agent  │  Agent  │  Agent   │   Agent     │
   └─────────┴─────────┴──────────┴─────────────┘
   ┌──────────┬───────────────────────────────────┐
   │ Timeline │       Remediation Agent             │
   │  Agent   │  (matches root cause → playbook)    │
   └──────────┴───────────────────────────────────┘
                      │
                      ▼
        GROQ AI — Llama 3.3 70B Versatile
   (Structured reasoning: ROOT_CAUSE, RISK_SCORE,
    FAILURE_CHAIN, REMEDIATION steps)
```

Six specialized agents inherit from a shared `BaseAgent` class and each call Groq's Llama 3.3 70B model with an engineered system prompt for their specific task — root cause analysis, risk scoring, correlation, timeline reconstruction, and remediation planning. Four of the six agents run concurrently via `asyncio.gather()` to minimize total investigation latency. The MCP Server sits between the agents and Splunk, exposing Splunk operations as discoverable tools rather than hardcoded API calls.

---

## 3. Data Flow Between Services, APIs, and Application Components

```
 1. Logs/Metrics        ──▶ Splunk Enterprise (HEC ingestion)
 2. Incident trigger    ──▶ AgentOrchestrator.investigate()
 3. QueryAgent          ──▶ Splunk REST API ──▶ raw telemetry (JSON)
 4. Telemetry           ──▶ RCA, Risk, Correlation, Timeline Agents
                              (run in parallel)
 5. Each Agent          ──▶ Groq API (Llama 3.3) ──▶ structured text
 6. Parsed outputs      ──▶ Remediation Agent ──▶ Remediation Engine
 7. Remediation Engine  ──▶ matches keyword ──▶ executes playbook
                              (memory_leak / high_cpu /
                               pod_crash / service_timeout)
 8. Full report         ──▶ Memory Manager (JSON store, last 500)
 9. Full report         ──▶ Splunk HEC (source=ai_ops_intelligence)
10. Report              ──▶ FastAPI REST API ──▶ Dashboard (port 8002)
11. Dashboard / Copilot ──▶ Streaming responses via Server-Sent Events
```

### Component Summary

| Component | Technology | Role |
|-----------|-----------|------|
| Splunk Enterprise | Splunk | Log storage, search, intelligence repository |
| MCP Server | Custom Python | Tool registry for agent-to-Splunk communication |
| Agent Orchestrator | Python asyncio | Coordinates 6 agents, parallel execution |
| AI Reasoning Engine | Groq API (Llama 3.3 70B) | Root cause, risk, correlation, remediation |
| Remediation Engine | Python | Keyword-matched auto-remediation playbooks |
| Memory Manager | JSON file store | Persists incident history (last 500) |
| REST API / Dashboard | FastAPI | Investigation trigger, copilot, history, health |
