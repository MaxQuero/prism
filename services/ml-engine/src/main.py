from fastapi import FastAPI
import os

app = FastAPI(title="Prism ML Engine")

@app.get("/")
def read_root():
    return {"status": "alive", "service": "ml-engine", "database_host": os.getenv("DATABASE_URL").split('@')[-1]}