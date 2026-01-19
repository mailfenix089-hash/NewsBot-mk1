FROM python:3.11-slim

WORKDIR /app

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Копировать requirements.txt
COPY requirements.txt .

# Установить зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копировать исходный код
COPY news_bot.py .
COPY advanced_bot.py .
COPY config_examples.py .

# Создать директорию для данных
RUN mkdir -p /app/data /app/logs

# Запустить бота
CMD ["python", "news_bot.py"]
