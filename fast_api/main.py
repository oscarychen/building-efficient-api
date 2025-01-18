from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_test():
    return {"Hello": "World"}