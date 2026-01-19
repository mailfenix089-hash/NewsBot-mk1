"""
Расширенные примеры использования Telegram News Bot
Фильтрация, сортировка, интеграция с другими сервисами
"""

# ==================== ФИЛЬТРАЦИЯ ПО КЛЮЧЕВЫМ СЛОВАМ ====================

class NewsFilter:
    """Фильтрация новостей по ключевым словам"""
    
    def __init__(self):
        self.include_keywords = []  # Включить если содержит
        self.exclude_keywords = []  # Исключить если содержит
    
    def set_include(self, keywords: list):
        """Добавить ключевые слова для включения"""
        self.include_keywords = [k.lower() for k in keywords]
    
    def set_exclude(self, keywords: list):
        """Добавить ключевые слова для исключения"""
        self.exclude_keywords = [k.lower() for k in keywords]
    
    def should_post(self, article: dict) -> bool:
        """Проверить должна ли новость быть опубликована"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        full_text = f"{title} {summary}".lower()
        
        # Проверка ИСКЛЮЧЕНИЙ (высший приоритет)
        for keyword in self.exclude_keywords:
            if keyword in full_text:
                return False
        
        # Если есть include_keywords, проверяем их
        if self.include_keywords:
            for keyword in self.include_keywords:
                if keyword in full_text:
                    return True
            return False
        
        return True


# ==================== РАСШИРЕННОЕ ЛОГИРОВАНИЕ ====================

import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_dir: str = "logs"):
    """Настроить логирование с ротацией файлов"""
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger('newsbot')
    logger.setLevel(logging.DEBUG)
    
    # Ротирующий file handler (максимум 5 файлов по 5MB)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'newsbot.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ==================== ИНТЕГРАЦИЯ С DISCORD ====================

"""
Если вы хотите публиковать в Discord канал одновременно:

import aiohttp
from aiohttp import FormData

class DiscordPoster:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def post_news(self, article: dict, source: dict):
        '''Отправить новость в Discord webhook'''
        
        embed = {
            "title": article['title'],
            "description": article['summary'],
            "url": article['link'],
            "color": 0x00FF00,  # Зеленый
            "fields": [
                {
                    "name": "Источник",
                    "value": source['name'],
                    "inline": True
                },
                {
                    "name": "Тип",
                    "value": source['type'],
                    "inline": True
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        payload = {"embeds": [embed]}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as resp:
                return resp.status == 204

# Использование в main news_bot:
# discord_poster = DiscordPoster("YOUR_DISCORD_WEBHOOK_URL")
# await discord_poster.post_news(article, source)
"""


# ==================== ИНТЕГРАЦИЯ С WEBHOOK ====================

"""
REST API для управления ботом (FastAPI):

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Глобальный reference к боту
current_bot = None

@app.post("/api/sources")
async def add_source(name: str, url: str, source_type: str):
    '''API для добавления источника'''
    try:
        added = current_bot.db.add_source(name, url, source_type)
        if added:
            return {"status": "success", "message": f"Source {name} added"}
        else:
            raise HTTPException(status_code=400, detail="Source already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
async def get_sources():
    '''Получить список источников'''
    sources = current_bot.db.get_active_sources()
    return {"sources": sources}

@app.post("/api/fetch")
async def trigger_fetch():
    '''Ручное получение новостей'''
    await current_bot.cmd_fetch_news_scheduled()
    return {"status": "fetching"}

@app.get("/api/stats")
async def get_stats():
    '''Получить статистику'''
    return current_bot.advanced_bot.stats if hasattr(current_bot, 'advanced_bot') else {}

# Запуск:
# uvicorn app:app --host 0.0.0.0 --port 8000
"""


# ==================== АНАЛИЗ НОВОСТЕЙ (NLP) ====================

"""
Добавляем категоризацию и анализ тональности (требует textblob):

pip install textblob

from textblob import TextBlob
from collections import Counter

class NewsAnalyzer:
    '''Анализ новостей с помощью NLP'''
    
    KEYWORDS_MAPPING = {
        'positive': ['хорошо', 'успех', 'рост', 'выигрыш', 'улучшение'],
        'negative': ['плохо', 'падение', 'убыток', 'проблема', 'ошибка'],
        'security': ['уязвимость', 'безопасность', 'взлом', 'хак'],
        'crypto': ['криптовалюта', 'блокчейн', 'NFT', 'DeFi'],
        'ai': ['ИИ', 'нейросеть', 'машинное обучение', 'ChatGPT'],
    }
    
    @staticmethod
    def categorize(article: dict) -> list:
        '''Определить категории новости'''
        text = f"{article['title']} {article['summary']}".lower()
        categories = []
        
        for category, keywords in NewsAnalyzer.KEYWORDS_MAPPING.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories or ['general']
    
    @staticmethod
    def sentiment(text: str) -> str:
        '''Определить тональность (positive/neutral/negative)'''
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'

# Использование:
# categories = NewsAnalyzer.categorize(article)
# sentiment = NewsAnalyzer.sentiment(article['title'])
"""


# ==================== ПЛАНИРОВАНИЕ ПО ВРЕМЕННЫМ ЗОНАМ ====================

"""
Если нужна разная публикация в разных таймзонах:

from pytz import timezone
from datetime import datetime

class TimezonedScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.timezones = {
            'Moscow': 'Europe/Moscow',
            'London': 'Europe/London',
            'US-East': 'America/New_York',
            'US-West': 'America/Los_Angeles',
            'Tokyo': 'Asia/Tokyo',
        }
    
    def get_current_time(self, tz_name: str) -> datetime:
        '''Получить текущее время в таймзоне'''
        tz = timezone(self.timezones[tz_name])
        return datetime.now(tz)
    
    async def post_by_timezone(self, article: dict, source: dict, tz_name: str):
        '''Опубликовать если наступило правильное время'''
        current_time = self.get_current_time(tz_name)
        
        # Пример: публиковать только в 9:00
        if current_time.hour == 9:
            await self.bot._post_news_to_channels(article, source)

# Требует: pip install pytz
"""


# ==================== ДЕДУПЛИКАЦИЯ РАСШИРЕННАЯ ====================

"""
Умная дедупликация - проверка не только по URL, но и по содержимому:

import hashlib
from difflib import SequenceMatcher

class SmartDeduplicator:
    def __init__(self, db):
        self.db = db
    
    @staticmethod
    def hash_title(title: str) -> str:
        '''Хеш заголовка для сравнения'''
        return hashlib.md5(title.lower().strip().encode()).hexdigest()
    
    @staticmethod
    def similarity(str1: str, str2: str) -> float:
        '''Процент схожести двух строк'''
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    async def is_duplicate(self, article: dict, threshold: float = 0.8) -> bool:
        '''Проверить является ли дубликатом (по заголовку)'''
        
        # Сначала проверяем URL
        if self.db.is_news_published(article['link']):
            return True
        
        # Потом проверяем схожесть заголовков
        # ... (запрос всех последних новостей)
        # и сравнение с threshold
        
        return False
"""


# ==================== КЭШИРОВАНИЕ С REDIS ====================

"""
Для высокой нагрузки используйте Redis кэш:

pip install redis

import redis
import json

class RedisCache:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
    
    def cache_article(self, article: dict, ttl: int = 86400):
        '''Кэшировать статью на сутки'''
        key = f"article:{article['link']}"
        self.redis.setex(key, ttl, json.dumps(article))
    
    def get_cached_article(self, url: str) -> dict:
        '''Получить статью из кэша'''
        key = f"article:{url}"
        data = self.redis.get(key)
        return json.loads(data) if data else None
    
    def is_cached(self, url: str) -> bool:
        '''Проверить есть ли в кэше'''
        return self.redis.exists(f"article:{url}") > 0

# Использование:
# cache = RedisCache()
# cache.cache_article(article)
# if cache.is_cached(article['link']):
#     print("Статья в кэше, пропускаем")
"""


# ==================== ПРИМЕР ПОЛНОЙ ИНТЕГРАЦИИ ====================

"""
Полный пример с фильтрацией, логированием, и анализом:

from datetime import datetime
import asyncio

async def advanced_news_processor(bot, article, source):
    '''Продвинутая обработка новости перед публикацией'''
    
    logger = setup_logging()
    
    # 1. Фильтрация
    news_filter = NewsFilter()
    news_filter.set_include(['AI', 'machine learning', 'neural network'])
    
    if not news_filter.should_post(article):
        logger.info(f"Статья отфильтрована: {article['title']}")
        return
    
    # 2. Анализ
    # categories = NewsAnalyzer.categorize(article)
    # sentiment = NewsAnalyzer.sentiment(article['title'])
    # logger.info(f"Categories: {categories}, Sentiment: {sentiment}")
    
    # 3. Публикация
    await bot._post_news_to_channels(article, source)
    logger.info(f"✅ Опубликовано: {article['title']}")
    
    # 4. Кэширование (если используется)
    # cache = RedisCache()
    # cache.cache_article(article)
    
    # 5. В Discord (если используется)
    # await discord_poster.post_news(article, source)

# Интегрируем в основной бот:
# await advanced_news_processor(bot, article, source)
"""
