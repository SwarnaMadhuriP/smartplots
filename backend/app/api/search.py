from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.routing_service import SearchRoute, classify_search_query
from app.schemas.search import SmartSearchRequest, UnifiedSearchRequest
from app.services.search_service import run_agent_search, run_db_search

router = APIRouter()


@router.post("/search")
async def unified_search(
    request: UnifiedSearchRequest,
    db: Session = Depends(get_db),
):
    query = request.query.strip()
    route = classify_search_query(query)

    if route == SearchRoute.DB_SEARCH:
        return run_db_search(request, db)

    return await run_agent_search(request, db)


@router.post("/ai/search")
async def ai_search(request: SmartSearchRequest):
    unified = await run_agent_search(UnifiedSearchRequest(query=request.query))
    return {
        "response": unified["ai_summary"],
        "plots": unified["plots"],
        "filters": unified["filters"],
        "route": unified["route"],
    }
