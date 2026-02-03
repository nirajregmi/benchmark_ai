from dataclasses import dataclass

from app.report_gen.models.deployment_info import DeploymentInfo
from app.report_gen.models.request_composition_info import RequestCompositionInfo


@dataclass
class BenchmarkingInfo:
    """Benchmarking information for a specific test case."""
    story_name: str
    edit_name: str
    branch_name: str
    tba_claims: list[str]
    request_composition: list[RequestCompositionInfo]
    deployment_info: DeploymentInfo