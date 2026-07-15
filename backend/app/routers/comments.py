from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment, Post
from app.schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, comment_in: CommentCreate, db: Session = Depends(get_db)):
    # 대상 게시글 존재 여부 확인 (삭제되지 않은 활성 게시글만 대상)
    db_post = db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="대상 게시글을 찾을 수 없습니다.")
        
    db_comment = Comment(
        post_id=post_id,
        content=comment_in.content,
        author=comment_in.author,
        password=comment_in.password  # 평문 비밀번호 저장
    ) 
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, password_in: str, db: Session = Depends(get_db)):
    # 삭제되지 않은 댓글만 조회
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.is_deleted == False).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
        
    # 평문 비밀번호 검증
    if db_comment.password != password_in:
        raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        
    # Soft delete 처리
    db_comment.is_deleted = True
    db.commit()
    return None
