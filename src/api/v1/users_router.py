import redis
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from db.db import get_session
from models.user import User
from schemas.users import UserCreate, UserToken, UserInDB
from typing import Any
from fastapi.responses import ORJSONResponse

app = FastAPI()

# Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# JWT configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


users_router: APIRouter = APIRouter()

@users_router.post(
    '/register',
    response_model=UserInDB,
)
def register_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_creating: UserCreate,
) -> UserInDB:
    
    # здесь в репозитории будет логика регистрации
    hashed_password: str = pwd_context.hash(user_creating.password)
    user = User(
        username=user_creating.username,
        password=hashed_password,
        email=user_creating.email,
    )

    # TODO проверить юзера перед сохранением, возвращать токен
    # db.add(user)
    # db.commit()
    # db.refresh(user)

    return UserInDB(
        id=1,
        username=user.username,
        email=user.email,
        is_active=1,
    )


# @users_router.post("/auth")
# def authenticate_user(form_data: OAuth2PasswordRequestForm, db: Session = Depends(get_session)):
#     # Retrieve the user from the database based on the provided username
#     user = db.query(User).filter(User.username == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid username or password")
#     # Generate an access token using JWT
#     access_token = create_access_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     # Store the access token in Redis for session management
#     redis_client.set(user.username, access_token)
#     return {"access_token": access_token, "token_type": "bearer"}


# @users_router.get("/protected")
# def protected_route(token: str = Depends(oauth2_scheme)):
#     # Verify the access token from Redis
#     username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])["sub"]
#     if not redis_client.get(username) == token:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return {"message": "Protected resource"}
