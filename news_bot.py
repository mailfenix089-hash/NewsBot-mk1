"""
Telegram News Bot с поддержкой RSS, Дзен и X/Twitter
Асинхронный бот на aiogram v3 с SQLite БД для отслеживания опубликованных новостей
"""

import asyncio
import sqlite3
import feedparser
import aiohttp
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from contextlib import asynccontextmanager
import logging
from typing import List, Dict, Optional
import json
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNELS = json.loads(os.getenv("TELEGRAM_CHANNELS", "[]"))  # ID каналов для публикации
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== БД ====================
class NewsDatabase:
    def __init__(self, db_file: str = "news_bot.db"):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        """Инициализация БД"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Таблица источников
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                url TEXT UNIQUE,
                type TEXT,
                active INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица опубликованных новостей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS published_news (
                id INTEGER PRIMARY KEY,
                source_id INTEGER,
                title TEXT,
                url TEXT UNIQUE,
                published_at TIMESTAMP,
                posted_to_tg TIMESTAMP,
                FOREIGN KEY(source_id) REFERENCES sources(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_source(self, name: str, url: str, source_type: str = "rss") -> bool:
        """Добавить источник"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sources (name, url, type)
                VALUES (?, ?, ?)
            ''', (name, url, source_type))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_active_sources(self) -> List[Dict]:
        """Получить активные источники"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sources WHERE active = 1')
        sources = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return sources

    def is_news_published(self, url: str) -> bool:
        """Проверить, опубликована ли новость"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM published_news WHERE url = ?', (url,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def add_published_news(self, source_id: int, title: str, url: str, published_at: datetime):
        """Сохранить опубликованную новость"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO published_news (source_id, title, url, published_at, posted_to_tg)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (source_id, title, url, published_at))
        conn.commit()
        conn.close()

    def remove_source(self, name: str) -> bool:
        """Деактивировать источник"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('UPDATE sources SET active = 0 WHERE name = ?', (name,))
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении источника: {e}")
            return False


# ==================== ПАРСЕРЫ ====================
class NewsParser:
    @staticmethod
    async def parse_rss(url: str) -> List[Dict]:
        """Парсить RSS feed"""
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                logger.warning(f"RSS feed может быть некорректным: {url}")
            
            articles = []
            for entry in feed.entries[:10]:  # Последние 10 статей
                articles.append({
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:500],
                    'published': entry.get('published', ''),
                    'source': feed.feed.get('title', 'Unknown')
                })
            return articles
        except Exception as e:
            logger.error(f"Ошибка при парсинге RSS {url}: {e}")
            return []

    @staticmethod
    async def parse_zen(zen_url: str) -> List[Dict]:
        """Парсить канал Яндекс.Дзен (через RSS feed Дзена)"""
        # Дзен предоставляет RSS по адресу: https://dzen.ru/feed/rss/?channel_name=CHANNEL_NAME
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(zen_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        feed = feedparser.parse(text)
                        
                        articles = []
                        for entry in feed.entries[:10]:
                            articles.append({
                                'title': entry.get('title', 'No title'),
                                'link': entry.get('link', ''),
                                'summary': entry.get('summary', '')[:500],
                                'published': entry.get('published', ''),
                                'source': 'Яндекс.Дзен'
                            })
                        return articles
        except Exception as e:
            logger.error(f"Ошибка при парсинге Дзена: {e}")
        return []

    @staticmethod
    async def parse_twitter_rss(twitter_user: str) -> List[Dict]:
        """Парсить твиты пользователя X/Twitter через RSS агрегатор"""
        # Используем сервис nitter.net для RSS питания
        try:
            rss_url = f"https://nitter.net/{twitter_user}/rss"
            return await NewsParser.parse_rss(rss_url)
        except Exception as e:
            logger.error(f"Ошибка при парсинге Twitter: {e}")
        return []


# ==================== ФСМ ====================
class AdminStates(StatesGroup):
    waiting_for_source_name = State()
    waiting_for_source_url = State()
    waiting_for_source_type = State()


# ==================== БОТ ====================
class NewsBot:
    def __init__(self, token: str):
        self.bot = Bot(token=token)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.db = NewsDatabase()
        self.parser = NewsParser()
        
        # Регистрация хендлеров
        self._register_handlers()

    def _register_handlers(self):
        """Регистрация всех хендлеров"""
        # Команды администратора
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_add_source, Command("add_source"))
        self.dp.message.register(self.cmd_remove_source, Command("remove_source"))
        self.dp.message.register(self.cmd_list_sources, Command("sources"))
        self.dp.message.register(self.cmd_fetch_news, Command("fetch"))
        
        # ФСМ обработчики
        self.dp.message.register(self.process_source_name, 
                                StateFilter(AdminStates.waiting_for_source_name))
        self.dp.message.register(self.process_source_url,
                                StateFilter(AdminStates.waiting_for_source_url))
        self.dp.message.register(self.process_source_type,
                                StateFilter(AdminStates.waiting_for_source_type))

    async def cmd_start(self, message: types.Message):
        """Команда /start"""
        await message.answer(
            "👋 Привет! Я бот для распространения новостей.\n\n"
            "Используй /help для списка команд."
        )

    async def cmd_help(self, message: types.Message):
        """Команда /help"""
        help_text = """
📋 Команды администратора:
/add_source - Добавить источник новостей
/remove_source - Удалить источник
/sources - Список активных источников
/fetch - Получить новости прямо сейчас
/help - Эта справка

📝 Поддерживаемые типы источников:
• rss - RSS feed
• zen - Яндекс.Дзен
• twitter - X/Twitter (через Nitter)
        """
        await message.answer(help_text)

    async def cmd_add_source(self, message: types.Message, state: FSMContext):
        """Начало добавления источника"""
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        await state.set_state(AdminStates.waiting_for_source_name)
        await message.answer("📝 Введите название источника (например: 'Habr', 'Дзен Криптовалюты'):")

    async def process_source_name(self, message: types.Message, state: FSMContext):
        """Обработка названия источника"""
        await state.update_data(name=message.text)
        await state.set_state(AdminStates.waiting_for_source_url)
        await message.answer("🔗 Введите URL источника:\n\n"
                           "Примеры:\n"
                           "• RSS: https://example.com/feed\n"
                           "• Дзен: https://dzen.ru/feed/rss/?channel_name=channel_name\n"
                           "• Twitter: username (будет использован Nitter)")

    async def process_source_url(self, message: types.Message, state: FSMContext):
        """Обработка URL источника"""
        await state.update_data(url=message.text)
        await state.set_state(AdminStates.waiting_for_source_type)
        await message.answer("📌 Выберите тип источника:\n\n"
                           "1️⃣ rss\n"
                           "2️⃣ zen\n"
                           "3️⃣ twitter\n\n"
                           "Введите номер или тип:")

    async def process_source_type(self, message: types.Message, state: FSMContext):
        """Обработка типа источника"""
        type_map = {'1': 'rss', 'rss': 'rss', 
                   '2': 'zen', 'zen': 'zen',
                   '3': 'twitter', 'twitter': 'twitter'}
        
        source_type = type_map.get(message.text.lower())
        if not source_type:
            await message.answer("❌ Неверный тип. Выберите из: rss, zen, twitter")
            return
        
        data = await state.get_data()
        added = self.db.add_source(data['name'], data['url'], source_type)
        
        await state.clear()
        
        if added:
            await message.answer(f"✅ Источник '{data['name']}' добавлен!")
        else:
            await message.answer("❌ Ошибка: источник может быть уже добавлен")

    async def cmd_remove_source(self, message: types.Message):
        """Удалить источник"""
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        sources = self.db.get_active_sources()
        if not sources:
            await message.answer("📭 Нет активных источников")
            return
        
        text = "🗑 Выберите источник для удаления:\n\n"
        for i, source in enumerate(sources, 1):
            text += f"{i}. {source['name']} ({source['type']})\n"
        
        text += "\nОтправьте название источника:"
        await message.answer(text)

    async def cmd_list_sources(self, message: types.Message):
        """Список источников"""
        sources = self.db.get_active_sources()
        
        if not sources:
            await message.answer("📭 Нет активных источников")
            return
        
        text = "📋 Активные источники:\n\n"
        for source in sources:
            text += f"• {source['name']}\n"
            text += f"  Тип: {source['type']}\n"
            text += f"  URL: {source['url']}\n\n"
        
        await message.answer(text)

    async def cmd_fetch_news(self, message: types.Message):
        """Получить и опубликовать новости"""
        if message.from_user.id != ADMIN_ID:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        status = await message.answer("⏳ Загрузка новостей...")
        
        sources = self.db.get_active_sources()
        news_count = 0
        
        for source in sources:
            articles = []
            
            try:
                if source['type'] == 'rss':
                    articles = await self.parser.parse_rss(source['url'])
                elif source['type'] == 'zen':
                    articles = await self.parser.parse_zen(source['url'])
                elif source['type'] == 'twitter':
                    articles = await self.parser.parse_twitter_rss(source['url'])
                
                for article in articles:
                    if not self.db.is_news_published(article['link']):
                        await self._post_news_to_channels(article, source)
                        self.db.add_published_news(source['id'], article['title'], 
                                                 article['link'], datetime.now())
                        news_count += 1
                        await asyncio.sleep(1)  # Задержка между постами
            
            except Exception as e:
                logger.error(f"Ошибка при получении новостей из {source['name']}: {e}")
        
        await status.edit_text(f"✅ Опубликовано новостей: {news_count}")

    async def _post_news_to_channels(self, article: Dict, source: Dict):
        """Опубликовать новость в каналы"""
        message_text = f"""
📰 <b>{article['title']}</b>

ℹ️ Источник: {article['source']}
🏷️ Категория: {source['name']}

{article['summary']}

🔗 <a href="{article['link']}">Читать далее</a>
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Читать источник", url=article['link'])]
        ])
        
        for channel_id in CHANNELS:
            try:
                await self.bot.send_message(
                    chat_id=channel_id,
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке в канал {channel_id}: {e}")

    async def start_polling(self):
        """Запустить polling"""
        logger.info("🚀 Бот запущен!")
        await self.dp.start_polling(self.bot)


# ==================== MAIN ====================
async def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env")
    
    bot = NewsBot(TOKEN)
    await bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
