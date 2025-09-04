from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from models import User
from security import hash_password, verify_password, create_access_token, decode_token
from pydantic import EmailStr
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
#OAuth2PasswordBearer (grabs the token from requests) 
#tokenurl is the endpoint where people can login to get that token


@router.post("/register")
def register( email: EmailStr,name: str, password: str, role: str = "student", session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.email == email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(email=email, name= name, hashed_password=hash_password(password), role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email, "name":user.name ,"role": user.role}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user.id)) 
    return {"access_token": token, "token_type": "bearer", "user": user}


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    try:
        payload = decode_token(token)
        uid = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = session.get(User, uid)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
def require_roles(*roles: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep
@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role}