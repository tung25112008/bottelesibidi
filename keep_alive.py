from fastapi import FastAPI
import uvicorn
import threading
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Sibidi Bot is alive and running!"}

def run():
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
