import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from agent.pipeline import run_pipeline
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.post("/ask")
def ask(query: Query):
    response = run_pipeline(query.text)
    return {"response": response}

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)