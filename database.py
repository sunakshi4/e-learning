import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
load_dotenv()  # load variables from .env
DATABASE_URL = os.getenv("DATABASE_URL")  # now picks from .env
engine = create_engine(DATABASE_URL, echo=True)
def init_db():
    SQLModel.metadata.create_all(engine)
def get_session():
    with Session(engine) as session:
        yield session





