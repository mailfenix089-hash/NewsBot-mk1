"""
Advanced Telegram News Bot с автоматическим scheduler
Дополнительные возможности: статистика, логирование, обработка ошибок
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime

# Импортируем основной класс из news_bot.py
# from news_bot import NewsBot

logger = logging.getLogger(__name__)


class AdvancedNewsBot:
    """Расширенная версия бота с планировщиком"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.scheduler = AsyncIOScheduler()
        self.stats = {
            'fetches': 0,
            'news_posted': 0,
            'errors': 0,
            'last_fetch': None
        }

    def setup_schedule(self):
        """Настроить расписание автоматического получения новостей"""
        
        # Получение новостей каждые 30 минут
        self.scheduler.add_job(
            self.fetch_news_job,
            CronTrigger(minute='*/30'),
            id='fetch_every_30min',
            name='Fetch news every 30 minutes'
        )
        
        # Получение новостей в 9:00, 13:00 и 18:00 каждый день
        self.scheduler.add_job(
            self.fetch_news_job,
            CronTrigger(hour='9,13,18', minute='0'),
            id='fetch_scheduled',
            name='Fetch news at 9:00, 13:00, 18:00'
        )
        
        # Еженедельный отчет (каждый понедельник в 10:00)
        self.scheduler.add_job(
            self.send_weekly_report,
            CronTrigger(day_of_week='0', hour='10', minute='0'),
            id='weekly_report',
            name='Weekly statistics report'
        )
        
        logger.info("✅ Scheduler настроен")

    async def fetch_news_job(self):
        """Задача для автоматического получения новостей"""
        try:
            logger.info(f"🔄 Начало получения новостей в {datetime.now()}")
            
            sources = self.bot.db.get_active_sources()
            news_count = 0
            
            for source in sources:
                articles = []
                
                try:
                    if source['type'] == 'rss':
                        articles = await self.bot.parser.parse_rss(source['url'])
                    elif source['type'] == 'zen':
                        articles = await self.bot.parser.parse_zen(source['url'])
                    elif source['type'] == 'twitter':
                        articles = await self.bot.parser.parse_twitter_rss(source['url'])
                    
                    for article in articles:
                        if not self.bot.db.is_news_published(article['link']):
                            await self.bot._post_news_to_channels(article, source)
                            self.bot.db.add_published_news(
                                source['id'], 
                                article['title'],
                                article['link'], 
                                datetime.now()
                            )
                            news_count += 1
                            await asyncio.sleep(0.5)  # Задержка между постами
                
                except Exception as e:
                    logger.error(f"❌ Ошибка при получении новостей из {source['name']}: {e}")
                    self.stats['errors'] += 1
            
            self.stats['fetches'] += 1
            self.stats['news_posted'] += news_count
            self.stats['last_fetch'] = datetime.now()
            
            logger.info(f"✅ Получено и опубликовано новостей: {news_count}")
        
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в fetch_news_job: {e}")
            self.stats['errors'] += 1

    async def send_weekly_report(self):
        """Отправить еженедельный отчет администратору"""
        try:
            report_text = f"""
📊 <b>Еженедельный отчет новостного бота</b>

📈 Статистика:
• Количество запросов: {self.stats['fetches']}
• Опубликовано новостей: {self.stats['news_posted']}
• Ошибок: {self.stats['errors']}
• Последний запрос: {self.stats['last_fetch'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['last_fetch'] else 'N/A'}

👥 Активные источники: {len(self.bot.db.get_active_sources())}

⏰ Период: последние 7 дней
            """
            
            # Отправить администратору
            from os import getenv
            admin_id = int(getenv("ADMIN_ID", "0"))
            if admin_id:
                await self.bot.bot.send_message(
                    chat_id=admin_id,
                    text=report_text,
                    parse_mode="HTML"
                )
                logger.info("📊 Еженедельный отчет отправлен администратору")
        
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке отчета: {e}")

    async def get_stats(self):
        """Получить текущую статистику"""
        return {
            'fetches': self.stats['fetches'],
            'news_posted': self.stats['news_posted'],
            'errors': self.stats['errors'],
            'last_fetch': self.stats['last_fetch'].isoformat() if self.stats['last_fetch'] else None,
            'active_sources': len(self.bot.db.get_active_sources()),
            'uptime_seconds': (datetime.now() - datetime.now()).total_seconds()
        }

    def start(self):
        """Запустить планировщик"""
        self.setup_schedule()
        self.scheduler.start()
        logger.info("🚀 Scheduler запущен")

    def stop(self):
        """Остановить планировщик"""
        self.scheduler.shutdown()
        logger.info("⛔ Scheduler остановлен")


# ==================== Использование ====================
"""
В главном файле news_bot.py добавьте:

async def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env")
    
    bot = NewsBot(TOKEN)
    advanced_bot = AdvancedNewsBot(bot)
    
    # Запустить планировщик
    advanced_bot.start()
    
    # Запустить polling бота
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        advanced_bot.stop()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
"""
