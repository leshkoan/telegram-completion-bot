import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Settings:
    """Класс для хранения всех настроек проекта."""
    bot_token: str
    ollama_host: str
    ai_model: str
    max_tokens: int
    temperature: float
    top_p: float
    max_requests_per_minute: int
    log_level: str
    use_proxy: bool
    proxy_url: str | None

def load_settings() -> Settings:
    """Загружает настройки из .env файла."""
    load_dotenv()

    # Преобразование строки 'true'/'false' в bool
    use_proxy_str = os.getenv("USE_PROXY", "false").lower()
    use_proxy = use_proxy_str in ("true", "1", "yes")

    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        ai_model=os.getenv("AI_MODEL", "gpt2-oss:20b"),
        max_tokens=int(os.getenv("MAX_TOKENS", 100)),
        temperature=float(os.getenv("TEMPERATURE", 0.7)),
        top_p=float(os.getenv("TOP_P", 0.9)),
        max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", 5)),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        use_proxy=use_proxy,
        proxy_url=os.getenv("PROXY_URL") if use_proxy else None,
    )

# Загружаем настройки при импорте модуля
try:
    settings = load_settings()
    if not settings.bot_token:
        raise ValueError("BOT_TOKEN не найден в .env файле. Пожалуйста, добавьте его.")
except (ValueError, TypeError) as e:
    logging.basicConfig(level=logging.INFO)
    logging.critical(f"Ошибка при загрузке конфигурации: {e}")
    exit(1)