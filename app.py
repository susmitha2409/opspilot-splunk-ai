import asyncio
import sys
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from agents.orchestrator import AgentOrchestrator

console = Console()

async def demo():
    console.print(Panel.fit(
        "🤖 [bold cyan]Autonomous AI Ops Platform[/bold cyan]\n"
        "Splunk + MCP + Groq + Multi-Agent",
        border_style="cyan"
    ))
    orch = AgentOrchestrator()
    trigger = {
        "service":  "payment-service",
        "severity": "CRITICAL",
        "message":  "Connection pool exhausted, DB timeouts spiking"
    }
    console.print("\n[yellow]Triggering autonomous investigation...[/yellow]\n")
    report = await orch.investigate(trigger)

    table = Table(title="AI Investigation Report", border_style="green")
    table.add_column("Field",  style="cyan",  no_wrap=True)
    table.add_column("Result", style="white")
    table.add_row("Root Cause",      str(report["root_cause"].get("root_cause",       "N/A")))
    table.add_row("Confidence",      str(report["root_cause"].get("confidence",        "N/A")) + "%")
    table.add_row("Risk Score",      str(report["risk"].get("risk_score",              "N/A")) + "/100")
    table.add_row("Severity",        str(report["risk"].get("severity",                "N/A")))
    table.add_row("Next Failure",    str(report["risk"].get("predicted_next_failure",  "N/A")))
    table.add_row("Failure Chain",   str(report["correlations"].get("failure_chain",   "N/A")))
    table.add_row("Immediate Fix",   str(report["remediation"].get("immediate_action", "N/A")))
    table.add_row("Playbook Status", str(report["remediation"].get("playbook_executed","N/A")))
    console.print(table)
    console.print("\n[green]Report saved to memory and Splunk.[/green]")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8002
        console.print(f"[cyan]Starting API on port {port}[/cyan]")
        console.print(f"[cyan]Dashboard: http://localhost:{port}/dashboard/[/cyan]")
        console.print(f"[cyan]API Docs:  http://localhost:{port}/docs[/cyan]")
        uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
    else:
        asyncio.run(demo())
