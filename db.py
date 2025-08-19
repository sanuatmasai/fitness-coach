from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine

# user class and models
class UserBase(SQLModel):
    username: str = Field(default=None)
    email: str | None = Field(default=None)
    age: int | None = Field(default=None)
    weight: int | None = Field(default=None)
    height: int | None = Field(default=None)
    goals: str | None = Field(default=None)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    secret_name: str
    password: str


class UserUpdate(UserBase):
    username: str | None = None
    email: str | None = None
    age: int | None = None
    weight: int | None = None
    height: int | None = None
    goals: str | None = None




# Workout class and models
class WorkoutBase(SQLModel):
    userId: int = Field(default=None)
    date: str | None = Field(default=None)
    meal: int | None = Field(default=None)
    calories: int | None = Field(default=None)
    macros: int | None = Field(default=None)


class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class WorkoutPublic(WorkoutBase):
    id: int





sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]