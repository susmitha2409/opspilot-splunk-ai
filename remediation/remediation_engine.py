from config.logging_config import get_logger

logger = get_logger("RemediationEngine")

class RemediationEngine:
    def __init__(self):
        from remediation.playbooks import high_cpu, memory_leak, pod_crash, service_timeout
        self.registry = {
            "cpu":        high_cpu.execute,
            "memory":     memory_leak.execute,
            "memory leak":memory_leak.execute,
            "pod":        pod_crash.execute,
            "crash":      pod_crash.execute,
            "timeout":    service_timeout.execute,
            "connection": service_timeout.execute,
            "pool":       memory_leak.execute,
            "database":   service_timeout.execute,
            "db":         service_timeout.execute,
            "exhausted":  memory_leak.execute,
            "latency":    service_timeout.execute,
            "leak":       memory_leak.execute,
            "overload":   high_cpu.execute,
        }

    async def execute(self, root_cause: str, risk_score: str) -> dict:
        try:
            score = int(str(risk_score).split("/")[0])
        except:
            score = 50  # default to medium if parsing fails

        cause_lower = str(root_cause).lower()
        matched_key = next((k for k in self.registry if k in cause_lower), None)

        if not matched_key:
            logger.warning(f"No playbook matched for: {root_cause}")
            return {
                "status":     "no_playbook",
                "cause":      root_cause,
                "suggestion": "Manual investigation required"
            }

        if score < 40:
            logger.info(f"Risk score {score} too low — skipping auto-execution")
            return {"status": "skipped", "reason": "low_risk", "score": score}

        logger.info(f"Executing playbook: {matched_key}")
        result = await self.registry[matched_key]()
        return {"status": "executed", "playbook": matched_key, "result": result}
