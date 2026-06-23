from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models.models import Review, Movie, User
from schemas import ReviewCreate, ReviewOut, ReviewUpdate
from core.deps import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])

# przelicz średnią ocenę filmu
def recompute_avg(db: Session, movie_id: int):
    avg = db.query(func.avg(Review.rating)).filter(Review.movie_id == movie_id).scalar()
    movie = db.get(Movie, movie_id)
    movie.avg_rating = round(avg, 2) if avg is not None else 0.0
    db.commit()

# recenzje danego filmu
@router.get("", response_model=list[ReviewOut])
def list_reviews(movie_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.movie_id == movie_id).all()

# dodaj recenzję jedna na film przez usera i przelicz średnią
@router.post("", response_model=ReviewOut, status_code=201)
def add_review(data: ReviewCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Movie, data.movie_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiego filmu")
    if db.query(Review).filter_by(user_id=user.id, movie_id=data.movie_id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Już oceniłeś ten film")
    review = Review(user_id=user.id, movie_id=data.movie_id, rating=data.rating, content=data.content)
    db.add(review); db.commit(); db.refresh(review)
    recompute_avg(db, data.movie_id)
    return review

# edytuj swoją recenzję i przelicz średnią
@router.put("/{review_id}", response_model=ReviewOut)
def update_review(review_id: int, data: ReviewUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if not review or review.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiej recenzji")
    review.rating = data.rating
    review.content = data.content
    db.commit(); db.refresh(review)
    recompute_avg(db, review.movie_id)
    return review

# usuń recenzję (właściciel albo admin) i przelicz średnią
@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nie ma takiej recenzji")
    if review.user_id != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "To nie twoja recenzja")
    movie_id = review.movie_id
    db.delete(review); db.commit()
    recompute_avg(db, movie_id)             # po usunięciu średnia się zmienia