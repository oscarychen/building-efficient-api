from fastapi import FastAPI

from apis.cars import router
from database import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router)
