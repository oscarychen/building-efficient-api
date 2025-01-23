from fastapi import FastAPI

from apis.cars import router

app = FastAPI()

app.include_router(router)
