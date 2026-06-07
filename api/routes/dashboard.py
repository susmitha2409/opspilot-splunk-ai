from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Ops Dashboard</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: 'Segoe UI', sans-serif; background:#0a0e1a; color:#e0e6f0; }

  .topbar {
    background:linear-gradient(90deg,#1a237e,#0d47a1);
    padding:16px 32px; display:flex;
    justify-content:space-between; align-items:center;
    border-bottom:2px solid #2962ff;
  }
  .topbar h1 { font-size:22px; color:#fff; }
  .topbar .badge {
    background:#2962ff; color:#fff;
    padding:4px 14px; border-radius:20px; font-size:13px;
  }
  .status-bar {
    background:#0d1b2a; padding:10px 32px;
    display:flex; gap:24px; font-size:13px;
    border-bottom:1px solid #1e2d40;
  }
  .status-dot { display:inline-block; width:8px; height:8px;
    border-radius:50%; margin-right:6px; }
  .green { background:#00e676; }
  .yellow { background:#ffea00; }
  .red { background:#ff1744; }

  .main { display:grid; grid-template-columns:1fr 1fr; gap:20px; padding:24px 32px; }
  .full-width { grid-column: 1 / -1; }

  .card {
    background:#0d1b2a; border:1px solid #1e2d40;
    border-radius:12px; padding:20px;
  }
  .card h2 {
    font-size:15px; color:#64b5f6; margin-bottom:16px;
    display:flex; align-items:center; gap:8px;
  }
  .card h2 .icon { font-size:18px; }

  input, select, textarea {
    width:100%; background:#0a1628; border:1px solid #1e3a5f;
    color:#e0e6f0; padding:10px 14px; border-radius:8px;
    font-size:14px; margin-bottom:12px; outline:none;
    font-family:'Segoe UI', sans-serif;
  }
  input:focus, select:focus, textarea:focus { border-color:#2962ff; }
  textarea { resize:vertical; min-height:80px; }

  button {
    background:linear-gradient(135deg,#1565c0,#2962ff);
    color:#fff; border:none; padding:11px 28px;
    border-radius:8px; cursor:pointer; font-size:14px;
    font-weight:600; transition:all 0.2s;
    width:100%; margin-top:4px;
  }
  button:hover { background:linear-gradient(135deg,#2962ff,#42a5f5); transform:translateY(-1px); }
  button:disabled { background:#1e2d40; cursor:not-allowed; transform:none; }
  button.secondary {
    background:transparent; border:1px solid #2962ff; color:#64b5f6;
  }

  .result-box {
    background:#060d18; border:1px solid #1e3a5f;
    border-radius:8px; padding:16px; font-family:'Courier New', monospace;
    font-size:13px; line-height:1.7; min-height:100px;
    max-height:300px; overflow-y:auto; white-space:pre-wrap;
    color:#a5d6a7;
  }
  .result-box.loading { color:#64b5f6; }
  .result-box.error   { color:#ef9a9a; }

  .metric-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
  .metric {
    background:#060d18; border:1px solid #1e3a5f;
    border-radius:10px; padding:16px; text-align:center;
  }
  .metric .value { font-size:32px; font-weight:700; color:#64b5f6; }
  .metric .label { font-size:12px; color:#78909c; margin-top:4px; }
  .metric .change { font-size:11px; margin-top:4px; }
  .up   { color:#ff5252; }
  .down { color:#69f0ae; }

  .incident-list { display:flex; flex-direction:column; gap:8px; }
  .incident-item {
    background:#060d18; border-left:3px solid #2962ff;
    border-radius:6px; padding:12px 16px;
    display:flex; justify-content:space-between; align-items:center;
    cursor:pointer; transition:background 0.2s;
  }
  .incident-item:hover { background:#0d1b2a; }
  .incident-item.critical { border-left-color:#ff1744; }
  .incident-item.high     { border-left-color:#ff6d00; }
  .incident-item.medium   { border-left-color:#ffea00; }
  .incident-item.low      { border-left-color:#69f0ae; }

  .sev-badge {
    padding:3px 10px; border-radius:12px; font-size:11px; font-weight:600;
  }
  .sev-CRITICAL { background:#ff1744; color:#fff; }
  .sev-HIGH     { background:#ff6d00; color:#fff; }
  .sev-MEDIUM   { background:#ffea00; color:#000; }
  .sev-LOW      { background:#69f0ae; color:#000; }

  .risk-bar-container { margin-top:8px; }
  .risk-bar-bg {
    background:#1e2d40; border-radius:4px; height:8px; overflow:hidden;
  }
  .risk-bar-fill {
    height:100%; border-radius:4px; transition:width 1s ease;
    background:linear-gradient(90deg,#2962ff,#ff1744);
  }

  .copilot-messages {
    background:#060d18; border:1px solid #1e3a5f;
    border-radius:8px; padding:16px; min-height:200px;
    max-height:280px; overflow-y:auto; margin-bottom:12px;
    font-size:14px; line-height:1.8;
  }
  .msg-user { color:#64b5f6; margin-bottom:8px; }
  .msg-ai   { color:#a5d6a7; margin-bottom:12px; }
  .msg-label { font-weight:700; font-size:12px; margin-bottom:2px; }

  .copilot-input-row { display:flex; gap:10px; }
  .copilot-input-row input { margin-bottom:0; flex:1; }
  .copilot-input-row button { width:auto; padding:10px 20px; }

  .tabs { display:flex; gap:4px; margin-bottom:16px; }
  .tab {
    padding:7px 18px; border-radius:6px; cursor:pointer;
    font-size:13px; background:#060d18; border:1px solid #1e3a5f;
    color:#78909c; transition:all 0.2s;
  }
  .tab.active { background:#1565c0; border-color:#2962ff; color:#fff; }

  .spl-result {
    background:#060d18; border:1px solid #1e3a5f; border-radius:8px;
    overflow:hidden; margin-top:12px;
  }
  .spl-table { width:100%; border-collapse:collapse; font-size:13px; }
  .spl-table th {
    background:#0d1b2a; padding:10px 14px;
    text-align:left; color:#64b5f6; font-weight:600;
    border-bottom:1px solid #1e2d40;
  }
  .spl-table td {
    padding:9px 14px; border-bottom:1px solid #0a1628;
    color:#cfd8dc;
  }
  .spl-table tr:hover td { background:#0d1b2a; }

  ::-webkit-scrollbar { width:6px; }
  ::-webkit-scrollbar-track { background:#0a0e1a; }
  ::-webkit-scrollbar-thumb { background:#1e3a5f; border-radius:3px; }

  .spinner {
    display:inline-block; width:14px; height:14px;
    border:2px solid #1e3a5f; border-top-color:#2962ff;
    border-radius:50%; animation:spin 0.8s linear infinite;
    margin-right:8px; vertical-align:middle;
  }
  @keyframes spin { to { transform:rotate(360deg); } }

  .empty-state { text-align:center; color:#37474f; padding:32px; font-size:14px; }
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <h1>🤖 Autonomous AI Ops Platform</h1>
  <div style="display:flex;gap:12px;align-items:center">
    <span style="color:#78909c;font-size:13px" id="clock"></span>
    <span class="badge">Splunk + Groq AI</span>
  </div>
</div>

<!-- STATUS BAR -->
<div class="status-bar">
  <span><span class="status-dot green"></span>AI Agents: Online</span>
  <span><span class="status-dot green"></span>Groq API: Connected</span>
  <span id="splunk-status"><span class="status-dot yellow"></span>Splunk: Checking...</span>
  <span><span class="status-dot green"></span>MCP Server: Ready</span>
  <span id="incident-count" style="margin-left:auto;color:#64b5f6">Total Incidents: 0</span>
</div>

<!-- METRICS ROW -->
<div style="padding:20px 32px 0">
  <div class="metric-grid">
    <div class="metric">
      <div class="value" id="m-investigated">0</div>
      <div class="label">Investigations Run</div>
    </div>
    <div class="metric">
      <div class="value" id="m-avg-risk" style="color:#ff9800">--</div>
      <div class="label">Avg Risk Score</div>
    </div>
    <div class="metric">
      <div class="value" id="m-remediated" style="color:#69f0ae">0</div>
      <div class="label">Auto-Remediated</div>
    </div>
    <div class="metric">
      <div class="value" id="m-mttr" style="color:#64b5f6">~28s</div>
      <div class="label">Avg MTTR</div>
    </div>
  </div>
</div>

<!-- MAIN GRID -->
<div class="main">

  <!-- INVESTIGATE PANEL -->
  <div class="card">
    <h2><span class="icon">🔍</span> Trigger Investigation</h2>
    <input type="text" id="inv-service" placeholder="Service name (e.g. payment-service)" value="payment-service">
    <select id="inv-severity">
      <option value="CRITICAL">🔴 CRITICAL</option>
      <option value="HIGH" selected>🟠 HIGH</option>
      <option value="MEDIUM">🟡 MEDIUM</option>
      <option value="LOW">🟢 LOW</option>
    </select>
    <textarea id="inv-message" placeholder="Describe the issue...">Connection pool exhausted, DB timeouts spiking</textarea>
    <button id="btn-investigate" onclick="runInvestigation()">
      🚀 Run Autonomous Investigation
    </button>
    <div id="inv-result" class="result-box" style="margin-top:14px">
Waiting for investigation trigger...
    </div>
  </div>

  <!-- AI COPILOT -->
  <div class="card">
    <h2><span class="icon">💬</span> AI Ops Copilot</h2>
    <div class="copilot-messages" id="copilot-msgs">
      <div class="empty-state">Ask the AI anything about your system...<br><br>
        Try: "Why would payment-service fail?"<br>
        or: "What causes DB connection pool exhaustion?"<br>
        or: "How do I fix a pod CrashLoopBackOff?"
      </div>
    </div>
    <div class="copilot-input-row">
      <input type="text" id="copilot-input"
        placeholder="Ask about incidents, logs, fixes..."
        onkeydown="if(event.key==='Enter') askCopilot()">
      <button onclick="askCopilot()" style="white-space:nowrap">Ask AI</button>
    </div>
  </div>

  <!-- RECENT INCIDENTS -->
  <div class="card">
    <h2><span class="icon">📋</span> Recent Incidents
      <button class="secondary" onclick="loadHistory()"
        style="width:auto;padding:5px 14px;font-size:12px;margin:0 0 0 auto">
        Refresh
      </button>
    </h2>
    <div class="incident-list" id="incident-list">
      <div class="empty-state">No incidents yet. Run an investigation above.</div>
    </div>
  </div>

  <!-- ANOMALY DETECTOR -->
  <div class="card">
    <h2><span class="icon">📡</span> Anomaly Detector</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
      <div>
        <label style="font-size:12px;color:#78909c">CPU %</label>
        <input type="number" id="an-cpu" value="20" placeholder="CPU %">
      </div>
      <div>
        <label style="font-size:12px;color:#78909c">Memory %</label>
        <input type="number" id="an-mem" value="40" placeholder="Memory %">
      </div>
      <div>
        <label style="font-size:12px;color:#78909c">Error Rate %</label>
        <input type="number" id="an-err" value="2" placeholder="Error rate">
      </div>
      <div>
        <label style="font-size:12px;color:#78909c">Latency (ms)</label>
        <input type="number" id="an-lat" value="120" placeholder="Latency ms">
      </div>
    </div>
    <button onclick="checkAnomaly()">🔬 Check for Anomaly</button>
    <div id="anomaly-result" class="result-box" style="margin-top:12px;min-height:60px">
Enter metrics above and click Check.
    </div>
  </div>

  <!-- SPL QUERY RUNNER -->
  <div class="card full-width">
    <h2><span class="icon">🔎</span> Splunk Log Analyser</h2>
    <div class="tabs">
      <div class="tab active" onclick="setQuery('error_rate')">Error Rate</div>
      <div class="tab" onclick="setQuery('top_errors')">Top Errors</div>
      <div class="tab" onclick="setQuery('ai_reports')">AI Reports</div>
      <div class="tab" onclick="setQuery('risk')">Risk Scores</div>
      <div class="tab" onclick="setQuery('custom')">Custom SPL</div>
    </div>
    <div style="display:flex;gap:10px">
      <input type="text" id="spl-query" style="margin-bottom:0"
        value='index=main level=ERROR | stats count by service | sort -count'>
      <button onclick="runSPL()" style="width:auto;padding:10px 20px;white-space:nowrap">
        ▶ Run Query
      </button>
    </div>
    <div id="spl-result" style="margin-top:14px">
      <div class="empty-state">Run a query to see results here.</div>
    </div>
  </div>

  <!-- RISK OVERVIEW -->
  <div class="card">
    <h2><span class="icon">⚠️</span> Risk Overview</h2>
    <div id="risk-overview">
      <div class="empty-state">Run investigations to see risk data.</div>
    </div>
  </div>

  <!-- SYSTEM HEALTH -->
  <div class="card">
    <h2><span class="icon">💚</span> System Health</h2>
    <div id="health-checks">
      <div style="margin-bottom:14px">
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
          <span>Groq AI</span><span id="hc-groq" style="color:#69f0ae">Checking...</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
          <span>Memory Store</span><span id="hc-memory" style="color:#69f0ae">Checking...</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
          <span>Remediation Engine</span><span id="hc-remed" style="color:#69f0ae">Ready</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
          <span>Anomaly Detector</span><span id="hc-anomaly" style="color:#69f0ae">Ready</span>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:13px">
          <span>Splunk HEC</span><span id="hc-splunk" style="color:#ffea00">Optional</span>
        </div>
      </div>
      <button class="secondary" onclick="checkHealth()" style="font-size:13px">
        Refresh Health
      </button>
    </div>
  </div>

</div>

<script>
// ── Clock ──────────────────────────────────────────────
function updateClock() {
  document.getElementById('clock').textContent =
    new Date().toLocaleTimeString('en-IN', {hour12:false});
}
setInterval(updateClock, 1000);
updateClock();

// ── SPL Query Presets ──────────────────────────────────
const SPL_PRESETS = {
  error_rate: 'index=main level=ERROR | stats count by service | sort -count',
  top_errors: 'index=main level=ERROR | head 20',
  ai_reports: 'index=main source=ai_ops_intelligence | head 10',
  risk:       'index=main source=ai_ops_intelligence | table _time service risk_score severity',
  custom:     ''
};
function setQuery(key) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  const q = SPL_PRESETS[key];
  if (q) document.getElementById('spl-query').value = q;
}

// ── Investigate ────────────────────────────────────────
async function runInvestigation() {
  const btn = document.getElementById('btn-investigate');
  const box = document.getElementById('inv-result');
  const service  = document.getElementById('inv-service').value.trim();
  const severity = document.getElementById('inv-severity').value;
  const message  = document.getElementById('inv-message').value.trim();

  if (!service) { box.textContent = 'ERROR: Please enter a service name.'; return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Investigating...';
  box.className = 'result-box loading';
  box.textContent = 'Agents initialising...\\nFetching telemetry from Splunk...\\n';

  try {
    const resp = await fetch('/incidents/investigate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({service, severity, message})
    });
    const data = await resp.json();
    const r = data.report;

    box.className = 'result-box';
    box.textContent = [
      '=== AI INVESTIGATION REPORT ===',
      '',
      'ROOT CAUSE:        ' + (r.root_cause?.root_cause       || 'N/A'),
      'AFFECTED SERVICES: ' + (r.root_cause?.affected_services|| 'N/A'),
      'CONFIDENCE:        ' + (r.root_cause?.confidence        || 'N/A') + '%',
      '',
      'RISK SCORE:        ' + (r.risk?.risk_score              || 'N/A') + '/100',
      'SEVERITY:          ' + (r.risk?.severity                || 'N/A'),
      'NEXT FAILURE:      ' + (r.risk?.predicted_next_failure  || 'N/A'),
      'TIME TO FAILURE:   ' + (r.risk?.time_to_failure         || 'N/A'),
      '',
      'FAILURE CHAIN:     ' + (r.correlations?.failure_chain   || 'N/A'),
      'BLAST RADIUS:      ' + (r.correlations?.blast_radius    || 'N/A'),
      '',
      'IMMEDIATE FIX:     ' + (r.remediation?.immediate_action || 'N/A'),
      'PLAYBOOK:          ' + JSON.stringify(r.remediation?.playbook_executed || 'N/A'),
      '',
      '==============================',
    ].join('\\n');

    updateMetrics(r);
    loadHistory();
  } catch(e) {
    box.className = 'result-box error';
    box.textContent = 'ERROR: ' + e.message + '\\n\\nMake sure API server is running:\\npython app.py api';
  }

  btn.disabled = false;
  btn.innerHTML = '🚀 Run Autonomous Investigation';
}

// ── Copilot ────────────────────────────────────────────
async function askCopilot() {
  const input = document.getElementById('copilot-input');
  const msgs  = document.getElementById('copilot-msgs');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';

  // Clear empty state
  if (msgs.querySelector('.empty-state')) msgs.innerHTML = '';

  msgs.innerHTML += `<div class="msg-user"><div class="msg-label">YOU</div>${q}</div>`;
  msgs.innerHTML += `<div class="msg-ai" id="streaming-msg"><div class="msg-label">AI COPILOT</div><span class="spinner"></span></div>`;
  msgs.scrollTop = msgs.scrollHeight;

  try {
    const resp = await fetch('/copilot/ask', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({question: q})
    });
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    const el = document.getElementById('streaming-msg');
    el.querySelector('.spinner')?.remove();
    el.innerHTML += '<span id="ai-text"></span>';
    const textEl = document.getElementById('ai-text');

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      textEl.textContent += decoder.decode(value);
      msgs.scrollTop = msgs.scrollHeight;
    }
    el.removeAttribute('id');
  } catch(e) {
    document.getElementById('streaming-msg').innerHTML =
      `<div class="msg-label">AI COPILOT</div>Error: ${e.message}`;
  }
}

// ── Anomaly Check ──────────────────────────────────────
function checkAnomaly() {
  const cpu = parseFloat(document.getElementById('an-cpu').value) || 0;
  const mem = parseFloat(document.getElementById('an-mem').value) || 0;
  const err = parseFloat(document.getElementById('an-err').value) || 0;
  const lat = parseFloat(document.getElementById('an-lat').value) || 0;
  const box = document.getElementById('anomaly-result');

  const alerts = [];
  if (cpu > 80)   alerts.push('🔴 CPU CRITICAL: ' + cpu + '% (threshold: 80%)');
  else if (cpu>60) alerts.push('🟡 CPU WARNING: ' + cpu + '% (threshold: 60%)');
  else             alerts.push('🟢 CPU Normal: ' + cpu + '%');

  if (mem > 85)   alerts.push('🔴 MEMORY CRITICAL: ' + mem + '% (threshold: 85%)');
  else if (mem>70) alerts.push('🟡 MEMORY WARNING: ' + mem + '%');
  else             alerts.push('🟢 Memory Normal: ' + mem + '%');

  if (err > 10)   alerts.push('🔴 ERROR RATE CRITICAL: ' + err + '% (threshold: 10%)');
  else if (err>5)  alerts.push('🟡 ERROR RATE WARNING: ' + err + '%');
  else             alerts.push('🟢 Error Rate Normal: ' + err + '%');

  if (lat > 2000) alerts.push('🔴 LATENCY CRITICAL: ' + lat + 'ms (threshold: 2000ms)');
  else if (lat>1000) alerts.push('🟡 LATENCY WARNING: ' + lat + 'ms');
  else             alerts.push('🟢 Latency Normal: ' + lat + 'ms');

  const hasAnomaly = alerts.some(a => a.includes('🔴') || a.includes('🟡'));
  box.className = 'result-box' + (hasAnomaly ? ' error' : '');
  box.textContent = alerts.join('\\n') + '\\n\\n' +
    (hasAnomaly ? '⚠️ ANOMALY DETECTED — Consider triggering investigation.' : '✅ All metrics within normal range.');
}

// ── SPL Query ──────────────────────────────────────────
async function runSPL() {
  const query = document.getElementById('spl-query').value.trim();
  const box   = document.getElementById('spl-result');
  if (!query) return;

  box.innerHTML = '<div class="empty-state"><span class="spinner"></span> Running query...</div>';

  try {
    const resp = await fetch('/incidents/history');
    const data = await resp.json();
    const incidents = data.incidents || [];

    if (incidents.length === 0) {
      box.innerHTML = '<div class="empty-state">No data yet. Run an investigation first, then re-run this query.</div>';
      return;
    }

    const rows = incidents.map(inc => ({
      Time:    inc.saved_at || '-',
      Service: inc.trigger?.service || '-',
      'Root Cause': (inc.root_cause?.root_cause || '-').substring(0, 50),
      'Risk Score': inc.risk?.risk_score || '-',
      Severity: inc.risk?.severity || '-',
      Remediation: inc.remediation?.playbook_executed?.status || '-',
    }));

    const cols = Object.keys(rows[0]);
    box.innerHTML = `
      <div class="spl-result">
        <table class="spl-table">
          <thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead>
          <tbody>
            ${rows.map(r=>`<tr>${cols.map(c=>`<td>${r[c]}</td>`).join('')}</tr>`).join('')}
          </tbody>
        </table>
      </div>
      <div style="font-size:12px;color:#37474f;margin-top:8px;padding:0 4px">
        ${rows.length} record(s) from incident memory
      </div>`;
  } catch(e) {
    box.innerHTML = '<div class="empty-state" style="color:#ef9a9a">Error: ' + e.message + '</div>';
  }
}

// ── Load History ───────────────────────────────────────
async function loadHistory() {
  try {
    const resp = await fetch('/incidents/history');
    const data = await resp.json();
    const incidents = data.incidents || [];
    const list = document.getElementById('incident-list');
    document.getElementById('incident-count').textContent =
      'Total Incidents: ' + incidents.length;

    if (incidents.length === 0) {
      list.innerHTML = '<div class="empty-state">No incidents yet.</div>';
      return;
    }

    list.innerHTML = incidents.slice().reverse().map(inc => {
      const sev = inc.risk?.severity || 'MEDIUM';
      const service = inc.trigger?.service || 'unknown';
      const cause = (inc.root_cause?.root_cause || 'Investigation pending').substring(0, 55);
      const time = new Date(inc.saved_at).toLocaleTimeString('en-IN');
      return `
        <div class="incident-item ${sev.toLowerCase()}" title="${cause}">
          <div>
            <div style="font-weight:600;font-size:14px">${service}</div>
            <div style="font-size:12px;color:#78909c;margin-top:2px">${cause}</div>
            <div style="font-size:11px;color:#37474f;margin-top:2px">${time}</div>
          </div>
          <span class="sev-badge sev-${sev}">${sev}</span>
        </div>`;
    }).join('');
  } catch(e) {
    document.getElementById('incident-list').innerHTML =
      '<div class="empty-state" style="color:#ef9a9a">API not running. Start with: python app.py api</div>';
  }
}

// ── Update Metrics ─────────────────────────────────────
function updateMetrics(report) {
  const count = parseInt(document.getElementById('m-investigated').textContent) || 0;
  document.getElementById('m-investigated').textContent = count + 1;

  const score = parseInt(report.risk?.risk_score) || 0;
  document.getElementById('m-avg-risk').textContent = score;
  document.getElementById('m-avg-risk').style.color =
    score >= 80 ? '#ff5252' : score >= 60 ? '#ff9800' : '#69f0ae';

  const status = report.remediation?.playbook_executed?.status;
  if (status === 'executed') {
    const r = parseInt(document.getElementById('m-remediated').textContent) || 0;
    document.getElementById('m-remediated').textContent = r + 1;
  }

  // Risk overview
  const ro = document.getElementById('risk-overview');
  ro.innerHTML = `
    <div style="margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px">
        <span>${report.trigger?.service}</span>
        <span style="color:${score>=80?'#ff5252':score>=60?'#ff9800':'#69f0ae'}">${score}/100</span>
      </div>
      <div class="risk-bar-bg"><div class="risk-bar-fill" style="width:${score}%"></div></div>
    </div>
    <div style="font-size:12px;color:#78909c">
      Next at risk: ${report.risk?.predicted_next_failure || 'N/A'}<br>
      Time to failure: ${report.risk?.time_to_failure || 'N/A'}
    </div>`;
}

// ── Health Check ───────────────────────────────────────
async function checkHealth() {
  try {
    const resp = await fetch('/health/');
    const data = await resp.json();
    document.getElementById('hc-groq').textContent =
      data.status === 'healthy' ? '✅ Online' : '❌ Offline';
    document.getElementById('hc-memory').textContent = '✅ Online';
  } catch(e) {
    document.getElementById('hc-groq').textContent = '❌ API Offline';
  }
}

// ── Init ───────────────────────────────────────────────
window.onload = () => {
  loadHistory();
  checkHealth();
  setInterval(loadHistory, 30000);
};
</script>
</body>
</html>
"""
