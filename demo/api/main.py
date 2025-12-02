from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Server is running. Welcome!"}


@app.get("/users")
def get_users():
    return {"user1": "user1", "user2": "user2"}
