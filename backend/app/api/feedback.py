from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os
from datetime import datetime

router = APIRouter()

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Set up feedback file logger
feedback_logger = logging.getLogger("smartplots.feedback")
feedback_logger.setLevel(logging.INFO)
if not feedback_logger.handlers:
    fh = logging.FileHandler("logs/feedback.log", encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    feedback_logger.addHandler(fh)


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    vote: str  # "up" or "down"


@router.post("/plots/{plot_id}/ask/feedback")
def submit_feedback(plot_id: int, request: FeedbackRequest):
    if request.vote not in ("up", "down"):
        raise HTTPException(status_code=400, detail="vote must be 'up' or 'down'")

    label = "THUMBS_UP" if request.vote == "up" else "INACCURATE_LAND_DATA"
    feedback_logger.info(
        f"plot_id={plot_id} | vote={label} | question={request.question!r} | answer_preview={request.answer[:120]!r}"
    )

    return {"status": "recorded", "vote": request.vote}
