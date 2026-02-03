from dataclasses import dataclass

@dataclass
class DeploymentInfo:
    """Deployment information for a specific test case."""
    cpu_limits: str
    memory_limits: str
    heap_size: str
    cpu_requests: str
    memory_requests: str