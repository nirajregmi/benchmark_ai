from docx import Document
from docx.shared import Inches

from app.report_gen.models.benchmark_data import BenchmarkData
from app.report_gen.models.benchmarking_info import BenchmarkingInfo
from app.report_gen.models.report_graphs import ReportGraphs


def create_deployment_table(doc, benchmark_info):
    dep_table = doc.add_table(rows=6, cols=2)
    dep_table.style = 'Table Grid'
    dep_hdr = dep_table.rows[0].cells

    dep_hdr[0].text = "Resource"
    dep_hdr[1].text = "Value"

    cpu_lim_row = dep_table.rows[1].cells
    cpu_lim_row[0].text = "resources.limits.cpu"
    cpu_lim_row[1].text = benchmark_info.deployment_info.cpu_limits

    mem_lim_row = dep_table.rows[2].cells
    mem_lim_row[0].text = "resources.limits.memory"
    mem_lim_row[1].text = benchmark_info.deployment_info.memory_limits

    heap_size_row = dep_table.rows[3].cells
    heap_size_row[0].text = "env.heapSize"
    heap_size_row[1].text = benchmark_info.deployment_info.heap_size

    cpu_req_row = dep_table.rows[4].cells
    cpu_req_row[0].text = "resources.requests.cpu"
    cpu_req_row[1].text = benchmark_info.deployment_info.cpu_requests

    mem_req_row = dep_table.rows[5].cells
    mem_req_row[0].text = "resources.requests.memory"
    mem_req_row[1].text = benchmark_info.deployment_info.memory_requests


def create_table(rows, cols, headers, data, doc, style='Table Grid'):
    # Calculate actual rows needed: header + data rows
    actual_rows = len(data) + 1  # +1 for header row
    table = doc.add_table(rows=actual_rows, cols=cols)
    table.style = style
    hdr_cells = table.rows[0].cells
    for i in range(cols):
        hdr_cells[i].text = headers[i]
    for i in range(len(data)):
        row_cells = table.rows[i + 1].cells
        for j in range(cols):
            row_cells[j].text = data[i][j]
    return table


def generate_word_report(release1: BenchmarkData, release2: BenchmarkData, benchmark_info: BenchmarkingInfo,
                         graphs: ReportGraphs, ai_analysis: str = None):
    """
    Improved Word report generation with robust attribute checks and modular table creation.
    """
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    available_width = section.page_width - section.left_margin - section.right_margin

    # Main title
    doc.add_heading("Pod Comparison Report", level=1)

    # Pod Names
    meta_p = doc.add_paragraph()
    meta_p.add_run("Pod 1: ").bold = True
    meta_p.add_run(f"{release1.pod_name}\n")
    meta_p.add_run("Pod 2: ").bold = True
    meta_p.add_run(f"{release2.pod_name}\n")
    meta_p.add_run("Analysis Period: ").bold = True
    meta_p.add_run("Last 1 hour\n")

    # AI Analysis Section (if provided)
    if ai_analysis:
        doc.add_page_break()
        doc.add_heading("AI-Powered Analysis", level=2)
        # Parse the AI analysis and add it to the document
        for line in ai_analysis.split('\n'):
            if line.startswith('## '):
                doc.add_heading(line[3:], level=3)
            elif line.startswith('# '):
                doc.add_heading(line[2:], level=2)
            elif line.strip():
                doc.add_paragraph(line)
    
    doc.add_page_break()

    doc.add_page_break()

    # Deployment Configuration Table
    doc.add_heading("Deployment Configuration", level=2)
    dep_config_table = create_table(None, 2, ['Resource', 'Value'], [
        ['resources.limits.cpu', benchmark_info.deployment_info.cpu_limits],
        ['resources.limits.memory', benchmark_info.deployment_info.memory_limits],
        ['env.heapSize', benchmark_info.deployment_info.heap_size],
        ['resources.requests.cpu', benchmark_info.deployment_info.cpu_requests],
        ['resources.requests.memory', benchmark_info.deployment_info.memory_requests],
    ], doc)

    # Pod 1 Metrics
    doc.add_heading(f"Pod 1: {release1.pod_name}", level=2)

    if graphs.before_memory_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("Memory Usage", level=3)
    doc.add_picture(get_image_stream(graphs.before_memory_usage_graph), width=available_width)
    if graphs.before_cpu_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Usage", level=3)
    doc.add_picture(get_image_stream(graphs.before_cpu_usage_graph), width=available_width)
    if graphs.before_cpu_throttling_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Throttling", level=3)
    doc.add_picture(get_image_stream(graphs.before_cpu_throttling_graph), width=available_width)

    # Pod 2 Metrics
    doc.add_heading(f"Pod 2: {release2.pod_name}", level=2)

    if graphs.after_memory_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("Memory Usage", level=3)
    doc.add_picture(get_image_stream(graphs.after_memory_usage_graph), width=available_width)
    if graphs.after_cpu_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Usage", level=3)
    doc.add_picture(get_image_stream(graphs.after_cpu_usage_graph), width=available_width)
    if graphs.after_cpu_throttling_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Throttling", level=3)
    doc.add_picture(get_image_stream(graphs.after_cpu_throttling_graph), width=available_width)

    # Return the Document object

    return doc


def get_image_stream(image_bytes: bytes):
    from io import BytesIO
    return BytesIO(image_bytes)
