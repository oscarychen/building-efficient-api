from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.cars import router
from database import lifespan

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "fastapi"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
