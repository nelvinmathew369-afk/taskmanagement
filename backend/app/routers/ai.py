from fastapi import APIRouter, HTTPException, status
from app.schemas import TaskExtractRequest, TaskExtractResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/tasks", tags=["AI Task Extraction"])


@router.post(
    "/extract",
    response_model=TaskExtractResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract structured task details using AI",
    description="Accepts plain-English instruction and returns structured task details using an LLM API (or mock fallback). Returns extracted details for user review without auto-saving."
)
async def extract_task_from_text(
    payload: TaskExtractRequest
):
    """
    Stage 2 AI Task Extraction:
    - Accepts plain-English instruction (e.g., 'Prepare the monthly Ticket report by 15 October 2026. This is high priority.').
    - Returns structured task details (title, priority, due_date, description).
    - If information is missing, uses documented defaults (Medium priority) or null for optional fields.
    - Never invents a due date. If ambiguous, sets due_date to null and populates clarification_needed.
    - Result is returned for review; save ONLY when client submits to POST /tasks.
    """
    try:
        extracted = await AIService.extract_task(payload.text)
        return extracted
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI extraction service encountered an error: {str(e)}"
        )
