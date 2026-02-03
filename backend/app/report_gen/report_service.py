from docx import Document

from app.report_gen.graph_service import line_chart_bytes
from app.report_gen.models.benchmark_data import BenchmarkData
from app.report_gen.models.report_graphs import ReportGraphs
from app.report_gen.models.benchmarking_info import BenchmarkingInfo
from app.report_gen.word_service import generate_word_report


class ReportService:
    def __init__(self):
        pass

    def generate_report(self, release1: BenchmarkData, release2: BenchmarkData, benchmark_info: BenchmarkingInfo, ai_analysis: str = None) -> Document:
        graphs: ReportGraphs = ReportGraphs(
            before_cpu_usage_graph=line_chart_bytes(release1.cpu_usage, f"{release1.pod_name} - CPU Usage", 'Time', 'CPU Usage (cores)', dpi=300, color='red'),
            after_cpu_usage_graph=line_chart_bytes(release2.cpu_usage, f"{release2.pod_name} - CPU Usage", 'Time', 'CPU Usage (cores)', dpi=300, color='blue'),
            before_memory_usage_graph=line_chart_bytes(release1.memory_usage, f"{release1.pod_name} - Memory Usage", 'Time', 'Memory Usage (bytes)', dpi=300, color='red'),
            after_memory_usage_graph=line_chart_bytes(release2.memory_usage, f"{release2.pod_name} - Memory Usage", 'Time', 'Memory Usage (bytes)', dpi=300, color='blue'),
            before_cpu_throttling_graph=line_chart_bytes(release1.cpu_throttling, f"{release1.pod_name} - CPU Throttling", 'Time', 'Throttling Rate', dpi=300, color='red'),
            after_cpu_throttling_graph=line_chart_bytes(release2.cpu_throttling, f"{release2.pod_name} - CPU Throttling", 'Time', 'Throttling Rate', dpi=300, color='blue')
        )
        doc_bytes = generate_word_report(release1, release2, benchmark_info, graphs, ai_analysis=ai_analysis)
        return doc_bytes