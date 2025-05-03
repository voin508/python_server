# swagger_server/logger.py

import logging  # Импортируем модуль для логирования
from logging_loki import LokiHandler  # Импортируем обработчик Loki

# Настройка логирования
logger = logging.getLogger("python-server")
logger.setLevel(logging.INFO)

# Добавляем обработчик для Loki
loki_handler = LokiHandler(
    url="http://loki:3100/loki/api/v1/push",  # URL Loki внутри Docker-сети
    tags={"application": "python-server"},
    version="1",
)
logger.addHandler(loki_handler)

# Добавление новой строки в конце файла
