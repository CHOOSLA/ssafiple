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
    sw_lat: Optional[float] = None,
    sw_lng: Optional[float] = None,
    ne_lat: Optional[float] = None,
    ne_lng: Optional[float] = None,
    center_lat: Optional[float] = None,
    center_lng: Optional[float] = None,
    skip: int = 0,
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
    if sw_lat is not None and ne_lat is not None:
        query = query.filter(Location.latitude >= sw_lat, Location.latitude <= ne_lat)
    if sw_lng is not None and ne_lng is not None:
        query = query.filter(Location.longitude >= sw_lng, Location.longitude <= ne_lng)
        
    # 같은 장소에 여러 핀이 겹치는 현상을 방지하기 위해 위도/경도 기준으로 그룹화
    query = query.group_by(Location.latitude, Location.longitude)
        
    if center_lat is not None and center_lng is not None:
        # SQLite 호환을 위해 단순 피타고라스 제곱합으로 거리 계산하여 가까운 순 정렬
        query = query.order_by(
            ((Location.latitude - center_lat) * (Location.latitude - center_lat)) +
            ((Location.longitude - center_lng) * (Location.longitude - center_lng))
        )
        
    from app.models import Post, Comment

    locs = query.offset(skip).limit(limit).all()

    result = []
    for loc in locs:
        post_query = db.query(Post).filter(Post.location_id == str(loc.id), Post.is_deleted == False)
        count = post_query.count()
        latest_posts = post_query.order_by(Post.created_at.desc()).limit(2).all()

        preview_list = []
        for p in latest_posts:
            comment_count = db.query(Comment).filter(Comment.post_id == p.id, Comment.is_deleted == False).count()
            snippet = p.content[:44] + '…' if p.content and len(p.content) > 44 else (p.content or '')
            preview_list.append({
                "id": p.id,
                "title": p.title,
                "snippet": snippet,
                "comment_count": comment_count
            })

        loc_dict = {
            "id": loc.id,
            "name": loc.name,
            "category": loc.category,
            "address": loc.address,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "image_url": loc.image_url,
            "description": loc.description,
            "name_en": loc.name_en,
            "address_en": loc.address_en,
            "post_count": count,
            "latest_posts": preview_list
        }
        result.append(loc_dict)
    return result

@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, db: Session = Depends(get_db)):
    db_loc = db.query(Location).filter(Location.id == location_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="관광지 정보를 찾을 수 없습니다.")
    return db_loc
