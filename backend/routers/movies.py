from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.models import Movie, MediaType
from schemas import MovieCreate, MovieOut
from core.deps import require_admin

router = APIRouter(prefix="/movies", tags=["movies"])

# lista filmów z wyszukiwaniem po tytule
@router.get("", response_model=list[MovieOut])
def list_movies(search: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Movie)
    if search:
        q = q.filter(Movie.title.ilike(f"%{search}%"))
    return q.order_by(Movie.id).all()

# szczegóły jednego filmu albo 404
@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiego filmu")
    return movie

# dodaj film 
@router.post("", response_model=MovieOut, status_code=201)
def create_movie(data: MovieCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    movie = Movie(**data.model_dump())     # media_type to już MediaType
    db.add(movie); db.commit(); db.refresh(movie)
    return movie

# edytuj film — tylko admin (pełna podmiana pól)
@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, data: MovieCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiego filmu")
    for key, value in data.model_dump().items():
        setattr(movie, key, value)          # nadpisz pola wartościami z body
    db.commit(); db.refresh(movie)
    return movie

# usuń film cascade
@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    movie = db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiego filmu")
    db.delete(movie); db.commit()