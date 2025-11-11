import logging
import aiohttp
from config import settings

logger = logging.getLogger(__name__)

class AIService:
    """
    Сервис для взаимодействия с API локальной нейросети Ollama.
    """
    def __init__(self):
        self.host = settings.ollama_host
        self.model = settings.ai_model
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        self.top_p = settings.top_p
        self.api_url = f"{self.host}/api/generate"
        self.timeout = aiohttp.ClientTimeout(total=60)

    async def complete_text(self, prompt: str) -> str | None:
        """
        Отправляет запрос на дополнение текста в Ollama.

        Args:
            prompt: Текст для дополнения.

        Returns:
            Дополненный текст или None в случае ошибки.
        """
        # Формируем инструкцию для модели на русском языке, чтобы повысить точность.
        prompt_template = (
            "Ты — полезный ассистент. "
            "Дополни следующее предложение на русском языке всего несколькими словами. "
            "Не добавляй никаких комментариев, объяснений или переводов. "
            f"Предложение: {prompt}"
        )

        payload = {
            "model": self.model,
            "prompt": prompt_template,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_tokens,
            },
        }

        logger.info(f"Отправка запроса в Ollama (модель: {self.model})")
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(self.api_url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    logger.info(f"Полный ответ от Ollama: {data}")
                    logger.info("Ответ от Ollama успешно получен.")
                    return data.get("response", "").strip()
        except aiohttp.ClientConnectorError:
            logger.error(f"Не удалось подключиться к Ollama по адресу {self.host}. Сервис запущен?")
            raise ConnectionError("OllamaServiceConnectionError")
        except aiohttp.ClientResponseError as e:
            logger.error(f"Ollama API вернул ошибку: {e.status} {e.message}")
            return None
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при обращении к Ollama: {e}")
            return None

# Создаем экземпляр сервиса
ai_service = AIService()
