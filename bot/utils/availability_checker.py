import logging
import aiohttp

logger = logging.getLogger(__name__)

async def check_telegram_api() -> bool:
    """
    Проверяет доступность Telegram API.
    Возвращает True, если API доступен, иначе False.
    """
    logger.info("Проверка доступности Telegram API...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.telegram.org',
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    logger.info("Telegram API доступен.")
                    return True
                else:
                    logger.warning(f"Telegram API вернул статус {resp.status}. Возможно, требуется прокси.")
                    return False
    except Exception as e:
        logger.warning(f"Не удалось подключиться к Telegram API. Ошибка: {e}. Рекомендуется использовать прокси.")
        return False

async def check_ollama_api(host: str) -> bool:
    """
    Проверяет доступность Ollama API.
    Возвращает True, если API доступен, иначе False.
    """
    logger.info(f"Проверка доступности Ollama API по адресу {host}...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(host, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                # Ollama возвращает текстовый ответ на GET /
                if resp.status == 200:
                    logger.info("Ollama API доступен.")
                    return True
                else:
                    logger.error(f"Ollama API вернул статус {resp.status}.")
                    return False
    except Exception as e:
        logger.error(f"Не удалось подключиться к Ollama API. Убедитесь, что Ollama запущен. Ошибка: {e}")
        return False
