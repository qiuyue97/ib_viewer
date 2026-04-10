from fastapi import APIRouter, HTTPException
from models import AccountSnapshot, ReturnMetrics
from ib_client import get_snapshot
from database import get_all_injections
from calculator import compute_returns

router = APIRouter()


@router.get("/snapshot", response_model=AccountSnapshot)
def snapshot():
    try:
        return get_snapshot()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"IB connection error: {e}")


@router.get("/returns", response_model=ReturnMetrics)
def returns():
    try:
        snap = get_snapshot()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"IB connection error: {e}")

    rows = get_all_injections()
    injections = [(row.injected_on, row.amount_cny) for row in rows]
    return compute_returns(injections, snap.total_value_cny)
