from docx import Document

from report_gen.models.benchmark_data import BenchmarkData
from report_gen.models.benchmarking_info import BenchmarkingInfo
from report_gen.models.report_graphs import ReportGraphs
from report_gen.word_service import generate_word_report
from report_gen.graph_service import line_chart_bytes


class ReportService:
    def __init__(self):
        pass

    def generate_report(self, release1: BenchmarkData, release2: BenchmarkData, benchmark_info: BenchmarkingInfo) -> Document:
        graphs: ReportGraphs = ReportGraphs(
            before_cpu_usage_graph=line_chart_bytes(release1.cpu_usage, "Before Optimization - CPU Usage", 'Time', 'CPU Usage (cores)', dpi=300, color='red'),
            after_cpu_usage_graph=line_chart_bytes(release2.cpu_usage, "After Optimization - CPU Usage", 'Time', 'CPU Usage (cores)'),
            before_memory_usage_graph=line_chart_bytes(release1.memory_usage, "Before Optimization - Memory Usage", 'Time', 'Memory Usage (MB)'),
            after_memory_usage_graph=line_chart_bytes(release2.memory_usage, "After Optimization - Memory Usage", 'Time', 'Memory Usage (MB)'),
            before_cpu_throttling_graph=line_chart_bytes(release1.cpu_throttling, "Before Optimization - CPU Throttling", 'Time', 'CPU Throttling (%)'),
            after_cpu_throttling_graph=line_chart_bytes(release2.cpu_throttling, "After Optimization - CPU Throttling", 'Time', 'CPU Throttling (%)')
        )
        doc_bytes = generate_word_report(release1, release2,benchmark_info, graphs)
        return doc_bytes