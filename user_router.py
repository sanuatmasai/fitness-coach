from typing import Annotated
from fastapi import HTTPException, Query, APIRouter
from sqlmodel import select
from db import User, UserCreate, UserPublic, UserUpdate, SessionDep


router = APIRouter(tags=["users"])


@router.post("/users/", response_model=UserPublic)
def create_users(hero: UserCreate, session: SessionDep):
    db_hero = User.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.get("/users/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@router.get("/users/{hero_id}", response_model=UserPublic)
def read_user(hero_id: int, session: SessionDep):
    hero = session.get(User, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(hero_id: int, hero: UserUpdate, session: SessionDep):
    hero_db = session.get(User, user_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

@router.delete("/users/{user_id}")
def delete_user(hero_id: int, session: SessionDep):
    hero = session.get(User, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}