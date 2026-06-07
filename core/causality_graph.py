import networkx as nx
from config.logging_config import get_logger

logger = get_logger("CausalityGraph")

class CausalityGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_dependency(self, source: str, target: str, weight: float = 1.0):
        self.graph.add_edge(source, target, weight=weight)

    def find_root_causes(self, failed_service: str) -> list:
        if failed_service not in self.graph:
            return [failed_service]
        ancestors = nx.ancestors(self.graph, failed_service)
        centrality = nx.betweenness_centrality(self.graph)
        return sorted(ancestors, key=lambda n: centrality.get(n, 0), reverse=True)[:3]

    def get_blast_radius(self, failed_service: str) -> list:
        if failed_service not in self.graph:
            return []
        return list(nx.descendants(self.graph, failed_service))

    def load_default_topology(self):
        edges = [
            ("database", "auth-service"),
            ("database", "user-service"),
            ("auth-service", "api-gateway"),
            ("user-service", "api-gateway"),
            ("api-gateway", "frontend"),
            ("cache", "user-service"),
            ("message-queue", "notification-service"),
            ("user-service", "message-queue"),
        ]
        for src, dst in edges:
            self.add_dependency(src, dst)
        logger.info("Default topology loaded")
