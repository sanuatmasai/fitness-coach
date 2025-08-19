from typing import Annotated
from fastapi import HTTPException, Query, APIRouter
from sqlmodel import select
from db import Nutrient, NutrientBase, NutrientPublic, SessionDep


router = APIRouter(tags=["Nutrient"])


@router.post("/nutrient/", response_model=NutrientPublic)
def create_users(hero: NutrientBase, session: SessionDep):
    db_hero = Nutrient.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.get("/nutrient/", response_model=list[NutrientPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Nutrient).offset(offset).limit(limit)).all()
    return heroes


@router.get("/nutrient/{user_id}", response_model=NutrientPublic)
def read_user(user_id: int, session: SessionDep):
    hero = session.get(Nutrient, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Nutrient not found")
    return hero


@router.patch("/nutrient/{user_id}", response_model=NutrientBase)
def update_user(user_id: int, hero: NutrientBase, session: SessionDep):
    hero_db = session.get(Nutrient, user_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Nutrient not found")
    hero_data = hero.model_dump(exclude_unset=True)
    hero_db.sqlmodel_update(hero_data)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

@router.delete("/nutrient/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    hero = session.get(Nutrient, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Nutrient not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}