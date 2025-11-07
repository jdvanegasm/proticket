from fastapi import FastAPI
from routes import events

app = FastAPI(title="ProTicket Business API")
app.include_router(events.router)

@app.get("/")
def root():
    return {"message": "Business Logic API running!"}