from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from core.config import settings
from core.security import ALGORITHM
from database import get_db
from models.models import User

# token w headerze
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# sprawdza  zalogowanego użytkownika z tokenu albo zwraca 401
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    err = HTTPException(status.HTTP_401_UNAUTHORIZED, "Nieprawidłowy token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise err
    user = db.get(User, user_id)
    if user is None:
        raise err
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Wymagane uprawnienia admina")
    return user