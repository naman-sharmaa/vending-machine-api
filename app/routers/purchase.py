from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    ChangeBreakdownResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.services import purchase_service

router = APIRouter()


@router.post("/purchase", response_model=PurchaseResponse)
def purchase(data: PurchaseRequest, db: Session = Depends(get_db)):
    try:
        result = purchase_service.purchase(db, data.item_id, data.cash_inserted)
        return PurchaseResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "item_not_found":
            raise HTTPException(status_code=404, detail="Item not found")
        if error_msg == "out_of_stock":
            raise HTTPException(
                status_code=400,
                detail={"error": "Item out of stock"},
            )
        if error_msg.startswith("insufficient_cash"):
            parts = error_msg.split("|")
            required = int(parts[1])
            inserted = int(parts[2])
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Insufficient cash",
                    "required": required,
                    "inserted": inserted,
                },
            )
        raise


@router.get("/purchase/change-breakdown", response_model=ChangeBreakdownResponse)
def change_breakdown(change: int = Query(..., ge=0)):
    return purchase_service.change_breakdown(change)
