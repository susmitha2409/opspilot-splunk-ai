import asyncio
from agents.query_agent import QueryAgent
from agents.rca_agent import RCAAgent
from agents.correlation_agent import CorrelationAgent
from agents.risk_agent import RiskAgent
from agents.timeline_agent import TimelineAgent
from agents.remediation_agent import RemediationAgent
from core.splunk_client import SplunkClient
from memory.memory_manager import MemoryManager
from config.logging_config import get_logger

logger = get_logger("Orchestrator")

class AgentOrchestrator:
    def __init__(self):
        self.splunk = SplunkClient()
        self.memory = MemoryManager()
        self.agents = {
            "query":       QueryAgent(),
            "rca":         RCAAgent(),
            "correlation": CorrelationAgent(),
            "risk":        RiskAgent(),
            "timeline":    TimelineAgent(),
            "remediation": RemediationAgent(),
        }

    async def investigate(self, trigger: dict) -> dict:
        logger.info(f"Investigation triggered: {trigger}")
        query_result = await self.agents["query"].run(trigger)
        rca, correlation, risk, timeline = await asyncio.gather(
            self.agents["rca"].run(query_result),
            self.agents["correlation"].run(query_result),
            self.agents["risk"].run(query_result),
            self.agents["timeline"].run(query_result),
        )
        remediation = await self.agents["remediation"].run({
            **query_result,
            "root_cause": rca.get("root_cause"),
            "risk_score":  risk.get("risk_score"),
        })
        report = {
            "trigger":      trigger,
            "telemetry":    query_result,
            "root_cause":   rca,
            "correlations": correlation,
            "risk":         risk,
            "timeline":     timeline,
            "remediation":  remediation,
        }
        await self.memory.save_incident(report)
        await self.splunk.send_event(report, source="ai_ops_intelligence")
        logger.info("Investigation complete")
        return report
