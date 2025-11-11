import html
import json
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Глобальный обработчик ошибок. Логирует ошибки и отправляет сообщение пользователю.
    """
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Собираем информацию для отладки
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    
    message = (
        "Произошла исключительная ситуация при обработке запроса\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Отправляем сообщение об ошибке пользователю, если это возможно
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🤖 К сожалению, произошла внутренняя ошибка. Мы уже работаем над этим.",
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке пользователю: {e}")

# В PTB v20+ нет отдельного logging middleware, логирование встраивается
# в хендлеры и error_handler, что уже сделано.
# Для более детального логирования можно было бы создать декоратор,
# но для данного ТЗ достаточно текущей реализации.
import traceback
