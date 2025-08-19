from typing import Annotated
from fastapi import HTTPException, Query, APIRouter
from sqlmodel import select
from db import Workout, WorkoutBase, WorkoutPublic, SessionDep


router = APIRouter(tags=["Workout"])


@router.post("/workout/", response_model=WorkoutPublic)
def create_users(hero: WorkoutBase, session: SessionDep):
    db_hero = Workout.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.get("/workout/", response_model=list[WorkoutPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Workout).offset(offset).limit(limit)).all()
    return heroes


@router.get("/workout/{user_id}", response_model=WorkoutPublic)
def read_user(user_id: int, session: SessionDep):
    hero = session.get(Workout, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="User not found")
    return hero


@router.patch("/workout/{user_id}", response_model=WorkoutBase)
def update_user(user_id: int, hero: WorkoutBase, session: SessionDep):
    hero_db = session.get(Workout, user_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Workout not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

@router.delete("/workout/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    hero = session.get(Workout, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Workout not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}