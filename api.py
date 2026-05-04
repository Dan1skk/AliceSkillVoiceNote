import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import crud
from weather_service import get_weather

WELCOME_IMAGE_ID = "1540737/169fd0c1b3d0adb51028"

def handle_dialog(data: dict, db: Session):
    user_id = data['session']['user_id']
    input_text = data['request'].get('original_utterance', '').lower().strip()
    is_new = data['session']['new']

    buttons = [
        "Что я записал сегодня?",
        "Показать все записи",
        "Что было вчера?",
        "Удалить по номеру",
        "Удали последнюю",
        "Помощь",
        "Погода"
    ]

    welcome_commands = ["привет", "старт", "начни", "начать", "помощь", "что ты умеешь", "команды", "здарова"]

    if input_text.startswith("погода"):
        city = input_text.replace("погода", "").strip()

        if not city:
            return "Какой город вас интересует? Скажите, например: 'Погода Самара'.", buttons, None

        weather_res = get_weather(city)
        return weather_res, buttons, None

    if is_new or any(word in input_text for word in welcome_commands):
        help_msg = (
            "Привет! Я твой голосовой дневник. Вот мои команды:\n\n"
            "• Записать: просто диктуй текст.\n"
            "• Сегодня: 'Что я записал сегодня?'.\n"
            "• Вчера: 'Что я писал вчера?'.\n"
            "• История: 'Покажи все записи' (последние 10).\n"
            "• Удалить конкретную: 'Удали вторую запись'.\n"
            "• Стереть последнюю: 'Удали последнюю'.\n\n"
            "Что сделаем?"
        )
        return help_msg, buttons, WELCOME_IMAGE_ID

    if "удалить по номеру" in input_text:
        return ("Чтобы удалить конкретную запись, сначала посмотри список за сегодня, "
                "а потом скажи: 'Удали номер 2' или 'Удали пятую'."), buttons, None

    if "удали" in input_text:
        numbers = re.findall(r'\d+', input_text)
        ordinals = {"перв": 0, "втор": 1, "трет": 2, "четверт": 3, "пят": 4, "шест": 5}
        found_idx = None

        for word, idx in ordinals.items():
            if word in input_text:
                found_idx = idx
                break

        if numbers:
            found_idx = int(numbers[0]) - 1

        if found_idx is not None:
            deleted = crud.delete_note_by_index(db, user_id, found_idx)
            if deleted:
                return f"Удалила запись №{found_idx + 1}: '{deleted.content}'", buttons, None
            return f"Записи под номером {found_idx + 1} сегодня нет в списке.", buttons, None

        deleted = crud.delete_last_note(db, user_id)
        if deleted:
            return f"Сделано! Удалила последнюю запись: '{deleted.content}'", buttons, None
        return "В дневнике пока пусто, удалять нечего.", buttons, None

    if "все" in input_text and ("записи" in input_text or "покажи" in input_text):
        notes = crud.get_all_notes(db, user_id, limit=10)
        if notes:
            formatted_notes = []
            # Показываем в обратном порядке (от старых к новым для списка)
            for i, n in enumerate(reversed(notes)):
                date_str = n.created_at.strftime("%d.%m %H:%M")
                formatted_notes.append(f"{i + 1}. [{date_str}] {n.content}")
            res = "Последние 10 записей:\n" + "\n".join(formatted_notes)
            return res, buttons, None
        return "В дневнике пока совсем пусто.", buttons, None

    if "вчера" in input_text:
        yesterday = datetime.now() - timedelta(days=1)
        notes = crud.get_notes_by_date(db, user_id, yesterday)
        if notes:
            formatted_notes = [f"• [{n.created_at.strftime('%H:%M')}] {n.content}" for n in notes]
            res = "Твои вчерашние записи:\n" + "\n".join(formatted_notes)
            return res, buttons, None
        return "Вчера ты ничего не записывал.", buttons, None

    if "что" in input_text and ("сегодня" in input_text or "записал" in input_text):
        notes = crud.get_notes_by_date(db, user_id, datetime.now())
        if notes:
            formatted_notes = []
            for i, n in enumerate(notes):
                time_str = n.created_at.strftime("%H:%M")
                formatted_notes.append(f"{i + 1}. [{time_str}] {n.content}")
            res = "Твои записи за сегодня:\n" + "\n".join(formatted_notes)
            return res, buttons, None
        return "За сегодня записей пока нет. Продиктуй что-нибудь!", buttons, None

    if input_text:
        clean_text = input_text.replace("запиши", "").strip()
        if not clean_text:
            return "Я слушаю. Что именно записать в дневник?", buttons, None
        crud.create_note(db, user_id, clean_text)
        return f"Записала: {clean_text}", buttons, None

    return "Не совсем поняла тебя. Скажи 'Помощь', и я подскажу команды.", buttons, None