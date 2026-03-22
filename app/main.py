from fastapi import FastAPI
from app.routes.research import router as research_router

app = FastAPI()
app.include_router(research_router)
