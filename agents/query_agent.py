from agents.base_agent import BaseAgent

class QueryAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        service = context.get("service", "*")
        query   = f'index=main service="{service}" | head 100'
        self.logger.info(f"Fetching telemetry for: {service}")
        try:
            results = await self.splunk.run_search(query)
        except Exception as e:
            self.logger.warning(f"Splunk unavailable: {e}. Using mock data.")
            results = [{
                "service": service,
                "level":   "ERROR",
                "message": context.get("message", "Unknown error")
            }]
        return {
            **context,
            "telemetry":  results,
            "log_count":  len(results)
        }
