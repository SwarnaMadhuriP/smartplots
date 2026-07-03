from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plot
from app.schemas.compare import CompareRequest
from app.services.comparison_service import run_comparison_analysis

router = APIRouter()


@router.post("/plots/compare")
def compare_plots(request: CompareRequest, db: Session = Depends(get_db)):
    plots_by_id = {
        plot.id: plot
        for plot in db.query(Plot).filter(Plot.id.in_(request.plot_ids)).all()
    }
    plots = [plots_by_id[plot_id] for plot_id in request.plot_ids if plot_id in plots_by_id]
    if not plots:
        raise HTTPException(status_code=400, detail="No plots found to compare.")

    try:
        return run_comparison_analysis(plots, request.goal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
