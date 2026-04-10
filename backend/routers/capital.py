from fastapi import APIRouter, HTTPException
from models import CapitalInjection, CapitalInjectionIn
from database import add_injection, get_all_injections, delete_injection

router = APIRouter()


@router.get("/capital", response_model=list[CapitalInjection])
def list_capital():
    rows = get_all_injections()
    return [CapitalInjection.model_validate(r) for r in rows]


@router.post("/capital", response_model=CapitalInjection, status_code=201)
def create_capital(body: CapitalInjectionIn):
    row = add_injection(body.amount_cny, body.injected_on, body.note)
    return CapitalInjection.model_validate(row)


@router.delete("/capital/{injection_id}", status_code=204)
def remove_capital(injection_id: int):
    if not delete_injection(injection_id):
        raise HTTPException(status_code=404, detail="Injection not found")
