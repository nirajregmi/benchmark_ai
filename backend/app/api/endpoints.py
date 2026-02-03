from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.orchestrator import IntelligenceOrchestrator
import structlog

router = APIRouter()
logger = structlog.get_logger()

# Dependency to get orchestrator (could be singleton)
def get_orchestrator():
    return IntelligenceOrchestrator()

@router.post("/chat/query")
async def chat_query(
    request: ChatRequest, 
    orchestrator: IntelligenceOrchestrator = Depends(get_orchestrator)
):
    """
    Stream a response to a user's natural language question about metrics.
    """
    logger.info("api_chat_query", message=request.message, selected_pods=request.selected_pods)
    
    async def event_generator():
        async for chunk in orchestrator.process_user_query(request.message, request.selected_pods):
            # SSE format: data: <content>\n\n
            if chunk:
                yield f"{chunk}"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/metrics/available")
async def get_available_metrics():
    return {
        "metrics": ["cpu", "memory", "network"],
        "operations": ["trend", "peak", "compare"]
    }

@router.get("/metrics/pods")
async def get_pods(
    orchestrator: IntelligenceOrchestrator = Depends(get_orchestrator)
):
    """
    Return list of available pods to populate frontend dropdowns.
    """
    # Access internal service directly or via orchestrator wrapper
    return {"pods": await orchestrator.prom_service.get_available_pods()}


@router.post("/report/generate")
async def generate_report_endpoint(
    request: ChatRequest,
):
    """
    Generate and download a DOCX report comparing two pods.
    """
    from app.services.report_bridge import ReportBridge
    
    bridge = ReportBridge()
    try:
        file_stream = await bridge.generate_comparison_report(request.selected_pods)
        return StreamingResponse(
            file_stream, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=benchmark_report.docx"}
        )
    except Exception as e:
        logger.error("report_generation_failed", error=str(e))
        return {"error": str(e)}
