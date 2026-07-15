import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Post
from app.schemas import PostCreate, PostUpdate, PostOut

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/posts", tags=["posts"])

@router.post("/upload-image", status_code=status.HTTP_200_OK)
def upload_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 비어 있습니다.")

    ext = Path(file.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        raise HTTPException(status_code=400, detail="지원되지 않는 이미지 형식입니다.")

    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / filename
    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"image_url": f"/uploads/{filename}"}

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(post_in: PostCreate, db: Session = Depends(get_db)):
    db_post = Post(
        title=post_in.title,
        content=post_in.content,
        author=post_in.author,
        password=post_in.password,  # 평문 저장 (요구사항)
        image_url=post_in.image_url,
        location_id=post_in.location_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

from typing import List, Optional

@router.get("/", response_model=List[PostOut])
def list_posts(location_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # 삭제되지 않은 게시글만 조회
    query = db.query(Post).filter(Post.is_deleted == False)
    if location_id:
        query = query.filter(Post.location_id == location_id)
    posts = query.offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    # 삭제되지 않은 게시글만 조회
    db_post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return db_post

@router.put("/{post_id}", response_model=PostOut)
def update_post(post_id: int, post_in: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 평문 비밀번호 검증
    if db_post.password != post_in.password:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    if post_in.title is not None:
        db_post.title = post_in.title
    if post_in.content is not None:
        db_post.content = post_in.content
        
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, password_in: str, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        
    # 평문 비밀번호 검증
    if db_post.password != password_in:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    # Soft delete 처리
    db_post.is_deleted = True
    
    # Cascade Soft delete: 연동된 모든 댓글도 soft delete 처리
    for comment in db_post.comments:
        comment.is_deleted = True
        
    db.commit()
    return None

@router.post("/{post_id}/verify", status_code=status.HTTP_200_OK)
def verify_post_password(post_id: int, password_in: str, db: Session = Depends(get_db)):
    """
    수정/삭제 전 비밀번호 검증 API
    """
    db_post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    if db_post.password != password_in:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    return {"status": "verified", "message": "비밀번호가 확인되었습니다."}
