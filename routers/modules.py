from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from database import get_session
from auth import get_current_user
from models import Module, Course, User
from auth import require_roles

router = APIRouter(prefix="/modules", tags=["modules"])

@router.post("", response_model=Module, status_code=201, dependencies=[Depends(require_roles("instructor"))])
def create_module(course_id: int, title: str, order: int = 0, content: str| None=None, video_url: str|None=None ,
                  session: Session = Depends(get_session),
                  user: User = Depends(get_current_user)               
):
    course= session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="u can add modules in your courses only")
    module = Module(course_id=course_id, title=title, order=order, content=content, video_url=video_url)
    session.add(module)
    session.commit()
    session.refresh(module)
    return module

@router.get("/by-course/{course_id}", response_model=List[Module])
def list_modules(course_id: int, session: Session = Depends(get_session),  user: User = Depends(get_current_user)):
    return session.exec(select(Module).where(Module.course_id == course_id).order_by(Module.order, Module.id)).all()

@router.delete("/{module_id}", status_code=204, dependencies=[Depends(require_roles("instructor"))])
def delete_module(module_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    module = session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    course = session.get(Course, module.course_id)
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="u can delete modules in your courses only")
    session.delete(module)
    session.commit()
