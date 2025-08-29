from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, Literal
from datetime import date
from pydantic import EmailStr
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer
class RoleEnum(str, Enum):
    student="student"
    instructor="instructor"

#user
class UserBase(SQLModel):
    name:Optional[str]=None
    email: EmailStr = Field(index=True, unique=True)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    role: RoleEnum= Field(index=True, default=RoleEnum.student)
class UserCreate(UserBase):
    password: str
    role: Optional[str]=RoleEnum.student


#course
class CourseBase(SQLModel):
    title: str
    description: Optional[str] = None
    instructor_id: Optional[int] = Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False))

class Course(CourseBase, table= True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CourseCreate(CourseBase):
    pass

#modules
class Module(SQLModel, table=True):
    id: Optional[int]= Field(default=None, primary_key=True)
    course_id: int= Field(sa_column=Column(Integer, ForeignKey("course.id", ondelete="CASCADE"), nullable=False))
    title:str
    order: int=0
    content: Optional[str]=None
    video_url: Optional[str]=None

#enrollment
class Enrollment(SQLModel, table=True):
    user_id: int= Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True, nullable=False))
    course_id: int= Field(sa_column=Column(Integer, ForeignKey("course.id", ondelete="CASCADE"), primary_key=True, nullable=False))
    created_at: datetime= Field(default_factory=datetime.now)

#quiz
class Quiz(SQLModel, table=True):
    id: Optional[int]= Field(default= None, primary_key=True)
    course_id: int= Field(sa_column=Column(Integer, ForeignKey("course.id", ondelete="CASCADE"), nullable=False))
    moudule_id: int= Field(sa_column=Column(Integer, ForeignKey("module.id", ondelete="CASCADE"), nullable=False))
    title: str

#question 
class Question(SQLModel, table=True):
    id: Optional[int]= Field(default= None, primary_key=True)
    quiz_id: int= Field(sa_column=Column(Integer, ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False))
    text: str
    order: int= 0

#choice
class Choice(SQLModel, table=True):
    id: Optional[int]= Field(default= None, primary_key=True)
    question_id: int= Field(sa_column=Column(Integer, ForeignKey("question.id", ondelete="CASCADE"), nullable=False))
    text: str
    is_correct: bool= False

#submission
class Submission(SQLModel, table=True):
    id: Optional[int]= Field(default= None, primary_key=True)
    quiz_id: int= Field(sa_column=Column(Integer, ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False))
    user_id: int= Field(sa_column=Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False))
    score:Optional[float]=None
    max_score: Optional[float]=None