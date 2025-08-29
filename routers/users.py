from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User, UserCreate
from auth import get_current_user, require_roles


router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[User], dependencies=[Depends(require_roles("instructor"))])
def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@router.delete("/{user_id}", status_code=204,dependencies=[Depends(require_roles("instructor"))]) # ADD AUTH 
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return None








