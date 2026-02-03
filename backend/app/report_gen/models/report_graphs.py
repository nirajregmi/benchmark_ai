from dataclasses import dataclass
@dataclass
class ReportGraphs:
    """Graphs data for report generation."""
    before_cpu_usage_graph: bytes
    after_cpu_usage_graph: bytes
    before_memory_usage_graph: bytes
    after_memory_usage_graph: bytes
    before_cpu_throttling_graph: bytes
    after_cpu_throttling_graph: bytes
