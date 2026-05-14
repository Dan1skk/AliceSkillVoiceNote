from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, get_db
from api import handle_dialog
import uvicorn

# Создаём таблицы при старте приложения
Base.metadata.create_all(bind=engine)
#qwe
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    response_text, buttons, image_id = handle_dialog(data, db)

    # Формируем тело ответа для Алисы
    response_body = {
        "text": response_text,
        "tts": response_text,  # Озвучка текста голосом Алисы
        "buttons": [{"title": b, "hide": True} for b in buttons],
        "end_session": False
    }

    # Добавляем карточку с изображением, если передан image_id
    if image_id:
        response_body["card"] = {
            "type": "BigImage",
            "image_id": image_id,
            "title": "Твой Голосовой Дневник",
            "description": response_text
        }

    return {
        "response": response_body,
        "version": "1.0"
    }

if __name__ == "__main__":
    # Запуск сервера на порту 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
