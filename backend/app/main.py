from fastapi import FastAPI

app = FastAPI()

data = []

@app.get("/")
def home():
    return {"message": "API is running 🚀"}

@app.get("/test")
def get_data():
    return data

@app.post("/test")
def create_data(name: str):
    item = {"id": len(data) + 1, "name": name}
    data.append(item)
    return item