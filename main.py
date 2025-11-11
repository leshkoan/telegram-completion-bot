import asyncio
import logging
import sys
import os

from telegram.ext import Application
from telegram.request import HTTPXRequest

from config import settings
from bot.handlers.start import start_handler, help_handler
from bot.handlers.completion import completion_handler
from bot.middleware.error_handler import error_handler
from bot.utils.availability_checker import check_telegram_api, check_ollama_api

async def main() -> None:
    """Точка входа в приложение."""
    # --- Настройка путей и логирования ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(script_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, "bot.log")

    log_level = logging.getLevelName(settings.log_level)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout)
        ],
    )
    logger = logging.getLogger(__name__)
    logger.info("--- Запуск бота ---")

    # --- Асинхронные проверки доступности API ---
    if not await check_ollama_api(settings.ollama_host):
        logger.critical("Ollama API недоступен. Завершение работы.")
        return

    use_proxy = settings.use_proxy
    if not use_proxy:
        if not await check_telegram_api():
            logger.warning("Telegram API недоступен напрямую. Попробуйте включить прокси в .env файле (USE_PROXY=true).")

    # --- Инициализация бота ---
    request = HTTPXRequest(
        proxy_url=settings.proxy_url if use_proxy else None,
        connect_timeout=30,
        read_timeout=30,
    )
    logger.info(f"Использование прокси: {use_proxy}, URL: {settings.proxy_url if use_proxy else 'нет'}")

    app = Application.builder().token(settings.bot_token).request(request).build()

    # Регистрация обработчиков
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(completion_handler)
    app.add_error_handler(error_handler)

    logger.info("Бот готов к работе...")

    # Запуск бота в асинхронном режиме
    try:
        async with app:
            await app.start()
            await app.updater.start_polling()
            logger.info("Бот успешно запущен и работает в режиме опроса.")
            # Приложение будет работать, пока не будет остановлено вручную (Ctrl+C)
            await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Получен сигнал остановки...")
    finally:
        logger.info("--- Остановка бота ---")
        # Корректное завершение работы
        if app.updater and app.updater.is_running:
            await app.updater.stop()
        if app.running:
            await app.stop()
        # app.shutdown() вызывается автоматически через 'async with'


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен.")