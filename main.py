from typing import Annotated
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from sqlmodel import select
from rag_chain import load_and_split_documents, create_retriever, create_rag_chain
import os
from db import create_db_and_tables, User, UserCreate, UserPublic, UserUpdate, SessionDep

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/users/", response_model=UserPublic)
def create_users(hero: UserCreate, session: SessionDep):
    db_hero = User.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/users/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/users/{hero_id}", response_model=UserPublic)
def read_user(hero_id: int, session: SessionDep):
    hero = session.get(User, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/users/{user_id}", response_model=UserPublic)
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

@app.delete("/users/{user_id}")
def delete_user(hero_id: int, session: SessionDep):
    hero = session.get(User, user_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


# In-memory storage for retriever for simplicity; in production, use persistent storage
global_retriever = None 

@app.post("/ingest/")
async def ingest_document(file: UploadFile = File(...)):
    global global_retriever
    try:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        documents = load_and_split_documents(file_location)
        global_retriever = create_retriever(documents)
        os.remove(file_location) # Clean up temp file
        return {"message": "Document ingested successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting document: {str(e)}")

@app.post("/query/")
async def query_rag(question: str):
    global global_retriever
    if global_retriever is None:
        raise HTTPException(status_code=400, detail="No document ingested yet. Please ingest a document first.")
    
    rag_chain = create_rag_chain(global_retriever)
    try:
        answer = rag_chain.invoke(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying RAG: {str(e)}")