from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Course, CourseCreate, User
from auth import get_current_user, require_roles

router= APIRouter(prefix="/courses", tags=["courses"])

@router.post("", response_model=Course, status_code=201, dependencies=[Depends(require_roles("instructor"))])
def create_course(payload: CourseCreate, session:Session = Depends(get_session), user: User=Depends(get_current_user)):
    instructor_id=user.id
    course=Course(title=payload.title, description=payload.description,instructor_id=instructor_id)
    # print("hello")
    session.add(course)
    session.commit()
    session.refresh(course)
    return course

@router.get("", response_model=List[Course])
def list_courses(instructor_id: Optional[int] = None, session: Session = Depends(get_session)):
    q = select(Course)
    if instructor_id is not None:
        q = q.where(Course.instructor_id == instructor_id)
    return session.exec(select(Course)).all()

@router.get("/{course_id}", response_model=Course)
def get_course(course_id: int, session: Session = Depends(get_session)):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.delete("/{course_id}", status_code=204, dependencies=[Depends(require_roles("instructor"))])
def delete_course(course_id: int, session: Session = Depends(get_session), user: User= Depends(get_current_user)):
    c = session.get(Course, course_id)
    if c.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="u cannot delete courses of other instructors")
    if not c:
        raise HTTPException(status_code=404, detail="course not found")
    session.delete(c)
    session.commit()
    