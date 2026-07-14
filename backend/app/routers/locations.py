from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Location
from app.schemas import LocationOut

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/", response_model=List[LocationOut])
def list_locations(
    category: Optional[str] = None, 
    q: Optional[str] = None, 
    limit: int = 500, 
    db: Session = Depends(get_db)
):
    query = db.query(Location)
    if category:
        query = query.filter(Location.category == category)
    if q:
        query = query.filter(
            (Location.name.contains(q)) | (Location.address.contains(q))
        )
    return query.limit(limit).all()

@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db)):
    db_loc = db.query(Location).filter(Location.id == location_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="관광지 정보를 찾을 수 없습니다.")
    return db_loc
