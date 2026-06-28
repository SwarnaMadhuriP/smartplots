from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plot
from app.schemas.ask import AskRequest
from app.services.ask_service import ask_about_plot as run_ask_about_plot

router = APIRouter()


@router.post("/plots/{plot_id}/ask")
def ask_about_plot(plot_id: int, request: AskRequest, db: Session = Depends(get_db)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    return run_ask_about_plot(plot, question, db)
