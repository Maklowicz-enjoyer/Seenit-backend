from models.models import MediaType
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):        # dane przychodzące przy rejestracji
    username: str; email: str; password: str; full_name: str | None = None

class UserOut(BaseModel):           # user zwracany klientowi (bez hasła!)
    id: int; username: str; email: str; full_name: str | None; role: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):             # odpowiedź po logowaniu
    access_token: str; token_type: str = "bearer"


class MovieCreate(BaseModel):
    title: str
    media_type: MediaType
    year: int | None = None
    director: str | None = None
    genre: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    country: str | None = None
   

class MovieOut(MovieCreate):
    id: int; avg_rating: float
    model_config = ConfigDict(from_attributes=True)


class WatchlistCreate(BaseModel):
    movie_id: int

class WatchlistOut(BaseModel):
    id: int; movie_id: int; watched: bool
    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    movie_id: int
    rating: float = Field(ge=1, le=10)         
    content: str | None = None

class ReviewOut(BaseModel):
    id: int; user_id: int; movie_id: int; rating: float; content: str | None
    model_config = ConfigDict(from_attributes=True)