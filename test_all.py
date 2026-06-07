import asyncio
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()

async def test_groq():
    """Test all 5 Groq API keys."""
    from config.settings import settings
    from groq import AsyncGroq

    console.print("\n[bold cyan]Testing Groq API Keys...[/bold cyan]")
    keys = settings.get_groq_keys()
    results = []

    for i, key in enumerate(keys, 1):
        try:
            client = AsyncGroq(api_key=key)
            resp = await client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": "Reply with OK only"}],
                max_tokens=5
            )
            answer = resp.choices[0].message.content.strip()
            results.append((f"Key {i}", "✅ WORKING", answer))
        except Exception as e:
            results.append((f"Key {i}", "❌ FAILED", str(e)[:40]))

    return results

async def test_agents():
    """Test all 6 agents."""
    console.print("\n[bold cyan]Testing All Agents...[/bold cyan]")
    from agents.query_agent       import QueryAgent
    from agents.rca_agent         import RCAAgent
    from agents.risk_agent        import RiskAgent
    from agents.correlation_agent import CorrelationAgent
    from agents.timeline_agent    import TimelineAgent
    from agents.remediation_agent import RemediationAgent

    context = {
        "service":  "payment-service",
        "severity": "HIGH",
        "message":  "DB timeout errors spiking",
        "telemetry": [],
        "log_count": 0
    }

    agents = [
        ("Query Agent",       QueryAgent()),
        ("RCA Agent",         RCAAgent()),
        ("Risk Agent",        RiskAgent()),
        ("Correlation Agent", CorrelationAgent()),
        ("Timeline Agent",    TimelineAgent()),
        ("Remediation Agent", RemediationAgent()),
    ]

    results = []
    for name, agent in agents:
        try:
            result = await agent.run(context)
            key_count = len(result.keys())
            results.append((name, "✅ WORKING", f"{key_count} fields returned"))
        except Exception as e:
            results.append((name, "❌ FAILED", str(e)[:40]))

    return results

async def test_anomaly():
    """Test anomaly detector."""
    console.print("\n[bold cyan]Testing Anomaly Detector...[/bold cyan]")
    from core.anomaly_detector import AnomalyDetector
    try:
        detector = AnomalyDetector()
        metrics = [
            {"cpu":20,"memory":40,"error_rate":1,"latency":100,"request_count":500},
            {"cpu":22,"memory":41,"error_rate":1,"latency":105,"request_count":510},
            {"cpu":21,"memory":39,"error_rate":2,"latency":98, "request_count":490},
            {"cpu":19,"memory":42,"error_rate":1,"latency":102,"request_count":505},
            {"cpu":20,"memory":40,"error_rate":1,"latency":100,"request_count":500},
            {"cpu":22,"memory":41,"error_rate":1,"latency":105,"request_count":510},
            {"cpu":21,"memory":39,"error_rate":2,"latency":98, "request_count":490},
            {"cpu":19,"memory":42,"error_rate":1,"latency":102,"request_count":505},
            {"cpu":20,"memory":40,"error_rate":1,"latency":100,"request_count":500},
            {"cpu":22,"memory":41,"error_rate":1,"latency":105,"request_count":510},
            {"cpu":99,"memory":95,"error_rate":80,"latency":9000,"request_count":10},
        ]
        detector.fit(metrics)
        anomalies = detector.detect(metrics)
        return [("Anomaly Detector", "✅ WORKING", f"{len(anomalies)} anomaly detected")]
    except Exception as e:
        return [("Anomaly Detector", "❌ FAILED", str(e)[:40])]

async def test_causality():
    """Test causality graph."""
    try:
        from core.causality_graph import CausalityGraph
        g = CausalityGraph()
        g.load_default_topology()
        causes = g.find_root_causes("api-gateway")
        blast  = g.get_blast_radius("database")
        return [("Causality Graph", "✅ WORKING", f"{len(causes)} causes, {len(blast)} blast")]
    except Exception as e:
        return [("Causality Graph", "❌ FAILED", str(e)[:40])]

async def test_memory():
    """Test memory manager."""
    try:
        from memory.memory_manager import MemoryManager
        mem = MemoryManager()
        await mem.save_incident({"test": "ping", "service": "test-service"})
        recent = await mem.get_recent(1)
        return [("Memory Manager", "✅ WORKING", f"{len(recent)} record saved/retrieved")]
    except Exception as e:
        return [("Memory Manager", "❌ FAILED", str(e)[:40])]

async def test_remediation():
    """Test remediation engine."""
    try:
        from remediation.remediation_engine import RemediationEngine
        engine = RemediationEngine()
        r1 = await engine.execute("memory leak detected", "75")
        r2 = await engine.execute("cpu overload", "85")
        r3 = await engine.execute("pod crash loop", "90")
        return [("Remediation Engine", "✅ WORKING",
                 f"memory:{r1['status']} cpu:{r2['status']} pod:{r3['status']}")]
    except Exception as e:
        return [("Remediation Engine", "❌ FAILED", str(e)[:40])]

async def test_orchestrator():
    """Test full pipeline."""
    try:
        from agents.orchestrator import AgentOrchestrator
        orch = AgentOrchestrator()
        report = await orch.investigate({
            "service": "test-service",
            "severity": "HIGH",
            "message": "connection timeout"
        })
        keys = list(report.keys())
        return [("Full Orchestrator", "✅ WORKING", f"Keys: {', '.join(keys)}")]
    except Exception as e:
        return [("Full Orchestrator", "❌ FAILED", str(e)[:40])]

async def main():
    console.print("\n[bold white on blue] AUTONOMOUS AI OPS — FULL SYSTEM TEST [/bold white on blue]\n")

    all_results = []

    # Run all tests
    all_results += await test_groq()
    all_results += await test_anomaly()
    all_results += await test_causality()
    all_results += await test_memory()
    all_results += await test_remediation()
    all_results += await test_agents()
    all_results += await test_orchestrator()

    # Display results table
    table = Table(title="Test Results", border_style="cyan")
    table.add_column("Component",  style="cyan",  no_wrap=True, width=25)
    table.add_column("Status",     style="white", width=14)
    table.add_column("Details",    style="white", width=45)

    passed = 0
    failed = 0
    for name, status, detail in all_results:
        table.add_row(name, status, detail)
        if "✅" in status:
            passed += 1
        else:
            failed += 1

    console.print(table)
    console.print(f"\n[green]✅ Passed: {passed}[/green]  [red]❌ Failed: {failed}[/red]")

    if failed == 0:
        console.print("\n[bold green]🎉 ALL SYSTEMS OPERATIONAL — READY FOR DEMO![/bold green]")
    else:
        console.print("\n[bold red]⚠️  Some components need attention.[/bold red]")

asyncio.run(main())
