from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc

from app.api.deps import get_db, get_current_user
from app.models.item import Item
from app.models.user import User
from app.schemas import ItemCreate, ItemUpdate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=List[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search by name contains"),
    sort_by: str = Query("created_at", pattern="^(name|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    skip: int = 0,
    limit: int = Query(10, le=100),
):
    stmt = select(Item)
    if q:
        stmt = stmt.where(Item.name.ilike(f"%{q}%"))
    if sort_by == "name":
        stmt = stmt.order_by(asc(Item.name) if order == "asc" else desc(Item.name))
    elif sort_by == "updated_at":
        stmt = stmt.order_by(asc(Item.updated_at) if order == "asc" else desc(Item.updated_at))
    else:
        stmt = stmt.order_by(asc(Item.created_at) if order == "asc" else desc(Item.created_at))
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))

@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("", response_model=ItemOut, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = Item(name=payload.name, description=payload.description, owner_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/{item_id}", response_model=ItemOut)
def replace_item(item_id: int, payload: ItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    item.name = payload.name
    item.description = payload.description
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    if payload.name is not None:
        item.name = payload.name
    if payload.description is not None:
        item.description = payload.description
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(item)
    db.commit()
    return
