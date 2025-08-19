from fastapi import FastAPI
from db import create_db_and_tables
import user_router
import rag_router


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Welcome to the API!"}

app.include_router(user_router.router)
app.include_router(rag_router.router)


