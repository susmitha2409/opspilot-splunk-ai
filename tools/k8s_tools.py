from config.logging_config import get_logger

logger = get_logger("K8sTools")

class K8sTools:
    async def get_pod_status(self, namespace: str = "default") -> dict:
        # In production: use kubernetes Python client
        logger.info(f"Getting pod status for namespace: {namespace}")
        return {
            "namespace": namespace,
            "pods": [
                {"name": "payment-service-abc", "status": "CrashLoopBackOff"},
                {"name": "auth-service-xyz",    "status": "Running"},
                {"name": "api-gateway-def",      "status": "Running"},
            ]
        }
