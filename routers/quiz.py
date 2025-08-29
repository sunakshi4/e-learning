from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict
from sqlmodel import Session, select
from database import get_session
from models import Quiz, Question, Course, Module, Choice, Submission
from auth import get_current_user,require_roles
from models import User, RoleEnum

router = APIRouter(prefix="/quiz", tags=["quiz"])
#instructor apis

#create quiz
@router.post("", response_model=Quiz, dependencies=[Depends(require_roles("instructor"))])
def create_quiz(course_id: int, title: str, module_id: int, session: Session= Depends(get_session)):
    # add instructor check
    if not session.get(Course, course_id):
        raise HTTPException(status_code=404, detail="course not found")
    q= Quiz(course_id=course_id, moudule_id=module_id, title=title)
    session.add(q)
    session.commit()
    session.refresh(q)
    return q

#delete quiz
@router.delete("{quiz_id}", status_code=204, dependencies=[Depends(require_roles("instructor"))])
def delete_quiz(quiz_id: int, session: Session = Depends(get_session), user: User= Depends(get_current_user)):
    quiz = session.get(Quiz, quiz_id)
    course = session.get(Course, quiz.course_id)
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="u cannot delete quiz of other instructors")
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")
    session.delete(quiz)
    session.commit()
    

#add question
@router.post("/{quiz_id}/questions", response_model= Question, dependencies=[Depends(require_roles("instructor"))])
def add_question(quiz_id: int, text: str, order:int = 0, session: Session= Depends(get_session)):
    # instructor auth
    if not session.get(Quiz, quiz_id):
        raise HTTPException(status_code=404, detail="quiz not found")
    q= Question(quiz_id=quiz_id, text=text, order=order)
    session.add(q)
    session.commit()
    session.refresh(q)
    return q

#delete question
@router.delete("{question_id}", status_code=204, dependencies=[Depends(require_roles("instructor"))])
def delete_question(question_id: int, session: Session = Depends(get_session), user: User= Depends(get_current_user)):
    question = session.get(Question, question_id)
    quiz = session.get(Quiz, question.quiz_id)
    course = session.get(Course, quiz.course_id)
    if course.instructor_id != user.id:
        raise HTTPException(status_code=403, detail="u cannot delete questions of other instructors")
    if not question:
        raise HTTPException(status_code=404, detail="question not found")
    session.delete(question)
    session.commit()

#add choice
@router.post("/questions/{question_id}/choices", response_model= Choice, dependencies=[Depends(require_roles("instructor"))])
def add_choice(question_id: int, text: str, is_correct:bool = False, session: Session= Depends(get_session)):
    if not session.get(Question, question_id):
        raise HTTPException(status_code=404, detail="question not found")
    
    if is_correct:
        existing= session.exec(
            select(Choice).where(Choice.question_id == question_id, Choice.is_correct == True)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail= " only 1 answer can be correct")
    c= Choice(question_id=question_id, text=text, is_correct=is_correct)
    session.add(c)
    session.commit()
    session.refresh(c)
    return c

#student apis
@router.get("", response_model= List[Quiz])
def list_all_quiz(session: Session= Depends(get_session)):
    return session.exec(select(Quiz)).all()


# @router.post("/{quiz_id}/start", response_model=Submission)
# def start_quiz(quiz_id: int, session: Session= Depends(get_session), user: User= Depends(get_current_user)):
#     quiz= session.get(Quiz, quiz_id)
#     if not quiz:
#         raise HTTPException(status_code=404, detail="quiz not found")
    
#     sub= Submission(quiz_id=quiz_id, user_id=user.id)
#     session.add(sub)
#     session.commit()
#     session.refresh(sub)
#     return sub

@router.post("/submissions/{quiz_id}/submit")
def submit_quiz(quiz_id: int, 
                answers: Dict[int, int] = Body(..., description="{question_id: choice_id}"),
                session: Session=Depends(get_session),
                user: User= Depends(get_current_user)
):
    quiz= session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")
    
    questions= session.exec(
        select(Question).where(Question.quiz_id == quiz_id)
    ).all()

    score=0
    max_score=0
    for q in questions:
        max_score=max_score+1
        ans_choice_id= answers.get(q.id)
        if ans_choice_id is None:
            continue
        choice= session.get(Choice, ans_choice_id)
        if choice.question_id!= q.id:
            raise HTTPException(status_code=400, detail="invalid")
        if choice.is_correct:
            score= score+1
    
    submission= Submission(quiz_id=quiz_id, user_id=user.id, score=score, max_score=max_score)
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission

@router.get("/submissions/me", response_model=list[Submission])
def all_submissions(session: Session= Depends(get_session), user: User= Depends(get_current_user)):
    return session.exec(
        select(Submission).where(Submission.user_id== user.id)
    ).all()

@router.get("submissions/{quiz_id}", dependencies=[Depends(require_roles("instructor"))])
def quiz_submissions(quiz_id: int, session: Session= Depends(get_session), user: User= Depends(get_current_user)):
    quiz= session.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="quiz not found")
    
    return session.exec(
        select(Submission).where(Submission.quiz_id== quiz_id)
    ).all()