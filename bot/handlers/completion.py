import logging
import time
from telegram import Update, constants
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.services.ai_service import ai_service
from bot.utils.validators import is_valid_text
from config import settings

logger = logging.getLogger(__name__)

async def rate_limit_user(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Проверяет, не превысил ли пользователь лимит запросов.
    Возвращает True, если лимит превышен, иначе False.
    """
    # Получаем данные пользователя или создаем, если их нет
    user_data = context.user_data
    if 'requests' not in user_data:
        user_data['requests'] = []

    now = time.time()
    # Удаляем старые запросы (старше минуты)
    user_data['requests'] = [req_time for req_time in user_data['requests'] if now - req_time < 60]

    # Проверяем количество запросов за последнюю минуту
    if len(user_data['requests']) >= settings.max_requests_per_minute:
        logger.warning(f"Пользователь {user_id} превысил лимит запросов.")
        return True  # Лимит превышен

    # Добавляем текущий запрос
    user_data['requests'].append(now)
    return False  # Лимит не превышен

async def completion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений для дополнения фразы."""
    user_id = update.effective_user.id
    
    if not is_valid_text(update):
        await update.message.reply_text("⚠️ Ошибка: Длина вашего сообщения должна быть от 1 до 500 символов и не состоять только из пробелов.")
        return

    if await rate_limit_user(user_id, context):
        await update.message.reply_text(
            f"⏳ Вы отправляете запросы слишком часто. "
            f"Пожалуйста, подождите немного. (Лимит: {settings.max_requests_per_minute} запросов в минуту)"
        )
        return

    user_text = update.message.text
    logger.info(f"Пользователь {user_id} отправил текст: '{user_text}'")

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)
        
        completion_text = await ai_service.complete_text(user_text)

        if completion_text is None:
            await update.message.reply_text("⚠️ Произошла непредвиденная ошибка при генерации ответа. Попробуйте изменить запрос.")
            return

        response_text = (
            f"*Ваша фраза:*\n`{user_text}`\n\n"
            f"*Продолжение:*\n{completion_text}"
        )
        await update.message.reply_text(response_text, parse_mode='Markdown')

    except ConnectionError:
        await update.message.reply_text("⚠️ Ошибка: Не удается подключиться к сервису нейросети. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка в обработчике completion: {e}")
        await update.message.reply_text("🤖 К сожалению, произошла внутренняя ошибка. Мы уже работаем над этим.")


# Создаем обработчик только для текстовых сообщений, которые не являются командами
completion_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, completion)
