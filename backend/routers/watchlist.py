from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Watchlist, Movie, User
from schemas import WatchlistCreate, WatchlistOut
from core.deps import get_current_user

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

# moja watchlista
@router.get("", response_model=list[WatchlistOut])
def my_watchlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Watchlist).filter(Watchlist.user_id == user.id).all()

# dodaj film do watchlisty
@router.post("", response_model=WatchlistOut, status_code=201)
def add(data: WatchlistCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Movie, data.movie_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiego filmu")
    if db.query(Watchlist).filter_by(user_id=user.id, movie_id=data.movie_id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Film już jest na liście")
    item = Watchlist(user_id=user.id, movie_id=data.movie_id)
    db.add(item); db.commit(); db.refresh(item)
    return item

# oznacz jako obejrzane
@router.patch("/{item_id}", response_model=WatchlistOut)
def mark_watched(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Watchlist, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiej pozycji")
    item.watched = True
    item.watched_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(item)
    return item

# usuń z watchlisty
@router.delete("/{item_id}", status_code=204)
def remove(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Watchlist, item_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiej pozycji")
    db.delete(item); db.commit()