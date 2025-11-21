from fastapi import FastAPI
from db import create_database, create_tables

from routes.users import router as user_router
from routes.logs import router as logs_router
from routes.premium import router as premium_router
from routes.limits import router as limits_router

app = FastAPI()

create_database()
create_tables()

app.include_router(user_router)
app.include_router(logs_router)
app.include_router(premium_router)
app.include_router(limits_router)

@app.get("/")
def home():
    return {"message": "Backend çalışıyor!"}
