from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, get_db
from api import handle_dialog

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    # Теперь handle_dialog возвращает кортеж (текст, кнопки)
    response_text, buttons = handle_dialog(data, db)

    return {
        "response": {
            "text": response_text,
            "buttons": [{"title": b, "hide": True} for b in buttons],
            "end_session": False
        },
        "version": "1.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)