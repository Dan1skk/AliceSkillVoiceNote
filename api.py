from datetime import datetime
from sqlalchemy.orm import Session
import crud


def handle_dialog(data: dict, db: Session):
    user_id = data['session']['user_id']
    input_text = data['request'].get('original_utterance', '').lower().strip()
    is_new = data['session']['new']

    # Кнопки для быстрого доступа
    buttons = ["Что я записал сегодня?", "Удали последнюю", "Помощь"]

    # 1. Приветствие
    if is_new:
        return "Привет! Я твой голосовой дневник. Что запишем или вспомним?", buttons

    # 2. Подробная справка по командам
    if "помощь" in input_text or "что ты умеешь" in input_text or "команды" in input_text:
        help_msg = (
            "Вот что я понимаю:\n\n"
            "1. Запись: Просто скажи фразу, например: 'Запиши сегодня отличная погода'.\n"
            "2. Просмотр: 'Что я записал сегодня?' или 'Прочитай мои записи'.\n"
            "3. Удаление: 'Удали последнюю запись' — если совершил ошибку.\n"
            "4. Выход: 'Хватит' или 'Выход', чтобы закончить работу.\n\n"
            "Что попробуем?"
        )
        return help_msg, buttons

    # 3. Удаление
    if "удали" in input_text:
        deleted = crud.delete_last_note(db, user_id)
        if deleted:
            return f"Окей, я стерла запись: '{deleted.content}'", buttons
        return "В дневнике пока пусто, удалять нечего.", buttons

    # 4. Просмотр записей за сегодня
    if "что" in input_text and ("сегодня" in input_text or "записал" in input_text or "записи" in input_text):
        notes = crud.get_notes_by_date(db, user_id, datetime.now())
        if notes:
            # Формируем список: [10:30] Текст заметки
            formatted_notes = []
            for n in notes:
                # Берём только часы и минуты из даты
                time_str = n.created_at.strftime("%H:%M")
                formatted_notes.append(f"• [{time_str}] {n.content}")

            res = "Твои записи за сегодня:\n" + "\n".join(formatted_notes)
            return res, buttons
        return "За сегодня записей пока нет. Хочешь что-нибудь добавить?", buttons

    # 5. Сохранение заметки
    if input_text:
        # Убираем лишнее слово 'запиши', если пользователь его использовал
        clean_text = input_text.replace("запиши", "").strip()

        if not clean_text:
            return "Я готова записать, но ты ничего не продиктовал. Что внести в дневник?", buttons

        crud.create_note(db, user_id, clean_text)
        return f"Поняла, записала: {clean_text}", buttons

    return "Не совсем поняла тебя. Попробуй сказать 'Помощь'.", buttons
