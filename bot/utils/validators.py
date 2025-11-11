from telegram import Update

def is_valid_text(update: Update) -> bool:
    """
    Проверяет, что текст сообщения от пользователя валиден.
    - Длина от 1 до 500 символов.
    - Не состоит только из пробелов.
    """
    if not update.message or not update.message.text:
        return False
        
    text = update.message.text.strip()
    return 1 <= len(text) <= 500
