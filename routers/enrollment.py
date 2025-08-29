from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from database import get_session
from models import Enrollment, Course
from auth import get_current_user,require_roles
from models import User, RoleEnum

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@router.get("/me", response_model=List[Enrollment])
def my_enrollments(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    return session.exec(select(Enrollment).where(Enrollment.user_id == user.id)).all()

@router.get("/my-courses", response_model=List[Enrollment], dependencies=[Depends(require_roles("instructor"))])
def enrollments_in_my_courses(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    q=(
        select(Enrollment)
        .join(Course,Course.id == Enrollment.course_id)
        .where(Course.instructor_id==user.id)
    )
    return session.exec(q).all()

@router.post("/enroll/{course_id}", status_code=201)
def enroll(course_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    if not session.get(Course, course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    if session.get(Enrollment, (user.id, course_id)):
        return {"message": "Already enrolled"}
    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    session.add(enrollment)
    session.commit()
    return {"message": "Enrolled"}

@router.post("/add/{course_id}/{student_id}", status_code=201,  dependencies=[Depends(require_roles("instructor"))])
def enroll_student_in_course(course_id: int,student_id=int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    course= session.get(Course, course_id)
    student= session.get(User, student_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403,detail=" u can only enroll students in your courses")
    if session.get(Enrollment, (user.id, course_id)):
        return {"message": "Already enrolled"}
    
    enrollment = Enrollment(user_id=student_id, course_id=course_id)
    session.add(enrollment)
    session.commit()
    return {"message": "Enrolled"}

@router.delete("/unenroll/{course_id}", status_code=204)
def self_unenroll(course_id: int, session:Session=Depends(get_session), user: User=Depends(get_current_user)):
    course= session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="course not found")
    enrollment= session.get(Enrollment, (user.id, course_id))
    if not enrollment:
        raise HTTPException(status_code=404, detail="U ARENT ENROLLED IN this course")
    session.delete(enrollment)
    session.commit()
    return

@router.delete("/{course_id}/students/{student_id}", status_code=204, dependencies=[Depends(require_roles("instructor"))])
def unenroll_student_from_course(course_id: int, student_id: int, session: Session= Depends(get_session), user: User=Depends(get_current_user)):
    course= session.get(Course, course_id)
    student= session.get(User, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    if not course:
        raise HTTPException(status_code=404, detail="course not found")
    if user.role == RoleEnum.instructor and course.instructor_id!= user.id:
        raise HTTPException(status_code=403,detail=" u can only unenroll students in your courses")
    enrollment= session.get(Enrollment, (student_id, course_id))
    if not enrollment:
        raise HTTPException(status_code=404, detail="student is not ENROLLED IN this course")
    session.delete(enrollment)
    session.commit()
    return









# @router.post("/complete/{course_id}")
# def complete(course_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
#     e = session.get(Enrollment, (user.id, course_id))
#     if not e: raise HTTPException(status_code=404, detail="Not enrolled")
#     e.status = "completed"; session.add(e); session.commit()
#     return {"message": "Marked completed"}

