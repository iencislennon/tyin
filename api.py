import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.pipeline import run_pipeline
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import logging

load_dotenv()
app = FastAPI()
import webbrowser
import threading

@app.on_event("startup")
async def open_browser():
    def _open():
        import time
        time.sleep(1)  # ждём пока сервер поднимется
        webbrowser.open("file:///Users/ansartleubayev/Desktop/creditagent/index.html")
    threading.Thread(target=_open, daemon=True).start()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Автообновление базы банков раз в неделю ──
def update_banks():
    try:
        logging.info("Запуск обновления базы банков...")
        from scraper.ingest import ingest_to_chroma
        ingest_to_chroma()
        logging.info("✓ База банков обновлена")
    except Exception as e:
        logging.error(f"Ошибка обновления базы: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(update_banks, 'interval', days=7)
scheduler.start()

class Query(BaseModel):
    text: str
    user_id: str = "default"

@app.post("/ask")
def ask(query: Query):
    response = run_pipeline(query.text, query.user_id)
    return {"response": response}

@app.get("/health")
def health():
    return {"status": "ok"}