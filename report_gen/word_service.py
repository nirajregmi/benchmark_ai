from docx import Document
from docx.shared import Inches

from report_gen.models.benchmark_data import BenchmarkData
from report_gen.models.benchmarking_info import BenchmarkingInfo
from report_gen.models.report_graphs import ReportGraphs


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
    table = doc.add_table(rows=rows, cols=cols)
    table.style = style
    hdr_cells = table.rows[0].cells
    for i in range(cols):
        hdr_cells[i].text = headers[i]
    for i in range(1, rows):
        row_cells = table.rows[i].cells
        for j in range(cols):
            row_cells[j].text = data[i - 1][j]
    return table


def generate_word_report(release1: BenchmarkData, release2: BenchmarkData, benchmark_info: BenchmarkingInfo,
                         graphs: ReportGraphs):
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
    doc.add_heading("Benchmark Report", level=1)

    # Story and Branch
    meta_p = doc.add_paragraph()
    meta_p.add_run("Story: ").bold = True
    meta_p.add_run(f"{benchmark_info.story_name}\n")
    meta_p.add_run("Test Branch: ").bold = True
    meta_p.add_run(f"{benchmark_info.branch_name}\n")

    # Requests
    req_p = doc.add_paragraph()
    req_p.add_run("Requests:").bold = True
    req_p.add_run("\nTBA Claims:\n")
    for claim in getattr(benchmark_info, 'tba_claims', []):
        req_p.add_run(f"    {claim}\n")

    # Request Composition Table
    doc.add_heading("Request Composition", level=2)
    req_table = create_table(
        9, 3,
        ["History count", "Hit data percentage array (20%)", "No Hit data percentage (80%)"],
        [
            [str(comp.history_count), str(comp.hit_data_percentage), str(comp.miss_data_percentage)]
            for comp in benchmark_info.request_composition
        ],
        doc
    )

    # Deployment Configuration Table
    doc.add_heading("Deployment Configuration", level=2)
    dep_config_table = create_table(6, 2, ['Resource', 'Value'], [
        ['resources.limits.cpu', benchmark_info.deployment_info.cpu_limits],
        ['resources.limits.memory', benchmark_info.deployment_info.memory_limits],
        ['env.heapSize', benchmark_info.deployment_info.heap_size],
        ['resources.requests.cpu', benchmark_info.deployment_info.cpu_requests],
        ['resources.requests.memory', benchmark_info.deployment_info.memory_requests],
    ], doc)

    # Version Comparison Table
    doc.add_heading("Before Implementing " + benchmark_info.edit_name, level=2)
    ver_table = create_table(4, 2, ['Project', 'Version'], [
        ['waah-rules',release1.waah_version],
        ['waah-taxonomy', release1.waah_taxonomy_version],
        ['waah-kernel', release1.waah_kernel_version],
    ], doc)

    # Before Implementation Metrics
    doc.add_heading("Metrics", level=2)

    if graphs.before_memory_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("Memory Usage Graph", level=3)
    doc.add_picture(get_image_stream(graphs.before_memory_usage_graph), width=available_width)
    if graphs.before_cpu_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Usage Graph", level=3)
    doc.add_picture(get_image_stream(graphs.before_cpu_usage_graph), width=available_width)
    if graphs.before_cpu_throttling_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Throttle Graph", level=3)
    doc.add_picture(get_image_stream(graphs.before_cpu_throttling_graph), width=available_width)

    # After Implementation Metrics
    doc.add_heading("After Implementing "+benchmark_info.edit_name, level=2)

    if graphs.after_memory_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("Memory Usage Graph", level=3)
    doc.add_picture(get_image_stream(graphs.after_memory_usage_graph), width=available_width)
    if graphs.after_cpu_usage_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Usage Graph", level=3)
    doc.add_picture(get_image_stream(graphs.after_cpu_usage_graph), width=available_width)
    if graphs.after_cpu_throttling_graph is not None:
        doc.add_paragraph()  # Add spacing
    doc.add_heading("CPU Throttle Graph", level=3)
    doc.add_picture(get_image_stream(graphs.after_cpu_throttling_graph), width=available_width)

    # Return the Document object

    return doc


def get_image_stream(image_bytes: bytes):
    from io import BytesIO
    return BytesIO(image_bytes)
