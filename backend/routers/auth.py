from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.models import User
from schemas import UserCreate, UserOut, Token
from core.security import hash_password, verify_password, create_access_token
from core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

#  tworzy użytkownika z zahashowanym hasłem
@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == data.username) | (User.email == data.email)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Login lub email zajęty")
    user = User(username=data.username, email=data.email,
                password_hash=hash_password(data.password), full_name=data.full_name)
    db.add(user); db.commit(); db.refresh(user)
    return user

#sprawdza hasło i zwraca token JWT
@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Zły login lub hasło")
    return Token(access_token=create_access_token(user.id))

# dane zalogowanego uzytkownika test
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

# edytuj własny profil 
@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.email is not None:
        taken = db.query(User).filter(User.email == data.email, User.id != user.id).first()
        if taken:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email zajęty")
        user.email = data.email
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password:
        user.password_hash = hash_password(data.password)   # hash_password już importujesz
    db.commit(); db.refresh(user)
    return user