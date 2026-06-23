from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from schemas import UserOut
from core.deps import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

# lista wszystkich użytkowników
@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.id).all()

# usuń użytkownika cascade
@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if user_id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nie możesz usunąć samego siebie")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiego użytkownika")
    db.delete(user); db.commit()