from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

# hash hasła przed zapisem do bazy
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# porównaj hasło z logowania z hashem z bazy
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# zbuduj token JWT
def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, algorithm=ALGORITHM)