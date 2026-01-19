"""
Примеры конфигураций и источников для Telegram News Bot
Готовые RSS feeds и Дзен каналы для быстрого старта
"""

# ===================== ПОПУЛЯРНЫЕ RSS FEEDS =====================

RSS_FEEDS = {
    # === РУССКОЯЗЫЧНЫЕ ИСТОЧНИКИ ===
    "Habr": {
        "url": "https://habr.com/ru/rss/all/",
        "description": "Все публикации на Хабре",
        "category": "tech"
    },
    "Habr Cryptography": {
        "url": "https://habr.com/ru/rss/hubs/cryptography/",
        "description": "Криптография на Хабре",
        "category": "crypto"
    },
    "Habr Security": {
        "url": "https://habr.com/ru/rss/hubs/information_security/",
        "description": "Безопасность на Хабре",
        "category": "security"
    },
    "Geektimes": {
        "url": "https://geektimes.ru/rss/all/",
        "description": "Все новости на Geektimes",
        "category": "tech"
    },
    "Opennet.ru News": {
        "url": "https://www.opennet.ru/opennews/opennews.rss",
        "description": "Новости от Opennet.ru",
        "category": "tech"
    },
    "4PDA News": {
        "url": "https://4pda.to/feed/",
        "description": "Новости мобильных технологий",
        "category": "mobile"
    },
    
    # === КРИПТОВАЛЮТЫ ===
    "CoinDesk": {
        "url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "description": "Новости криптовалют и blockchain",
        "category": "crypto"
    },
    "The Block Crypto": {
        "url": "https://www.theblock.co/rss.xml",
        "description": "Аналитика блокчейна",
        "category": "crypto"
    },
    
    # === МЕЖДУНАРОДНЫЕ ИСТОЧНИКИ ===
    "Hacker News": {
        "url": "https://news.ycombinator.com/rss",
        "description": "Hacker News (Англ)",
        "category": "tech"
    },
    "Python.org": {
        "url": "https://pythoninsider.blogspot.com/feeds/posts/default",
        "description": "Новости Python",
        "category": "programming"
    },
    "GitHub Blog": {
        "url": "https://github.blog/feed/",
        "description": "GitHub Official Blog",
        "category": "tech"
    },
    "Dev.to (Все)": {
        "url": "https://dev.to/feed",
        "description": "Сообщество Dev.to",
        "category": "programming"
    },
    "Medium (Tech)": {
        "url": "https://medium.com/feed/tag/technology",
        "description": "Статьи о технологиях",
        "category": "tech"
    },
    "ArXiv Computer Science": {
        "url": "http://arxiv.org/rss/cs.AI",
        "description": "Исследования по ИИ",
        "category": "ai"
    },
}

# ===================== ЯНДЕКС ДЗЕ КАНАЛЫ =====================

ZEN_CHANNELS = {
    # === ТЕХНОЛОГИИ ===
    "Технологии": {
        "channel_name": "technologies",
        "description": "Последние технологические новости",
        "url": "https://dzen.ru/feed/rss/?channel_name=technologies"
    },
    "Искусственный интеллект": {
        "channel_name": "artificial_intelligence",
        "description": "Новости в области ИИ",
        "url": "https://dzen.ru/feed/rss/?channel_name=artificial_intelligence"
    },
    "Кибербезопасность": {
        "channel_name": "cybersecurity",
        "description": "Новости безопасности",
        "url": "https://dzen.ru/feed/rss/?channel_name=cybersecurity"
    },
    "Криптовалюты": {
        "channel_name": "crypto_news",
        "description": "Новости крипто и блокчейна",
        "url": "https://dzen.ru/feed/rss/?channel_name=crypto_news"
    },
    
    # === БИЗНЕС И ЭКОНОМИКА ===
    "Стартапы": {
        "channel_name": "startups",
        "description": "Новости стартапов",
        "url": "https://dzen.ru/feed/rss/?channel_name=startups"
    },
    "Финтех": {
        "channel_name": "fintech",
        "description": "Финтеховские инновации",
        "url": "https://dzen.ru/feed/rss/?channel_name=fintech"
    },
}

# ===================== X/TWITTER АКАУНТЫ (Через Nitter) =====================

TWITTER_ACCOUNTS = {
    # === ТЕХНОЛОГИЯ И СТАРТАПЫ ===
    "elonmusk": {
        "description": "Илон Маск",
        "category": "tech"
    },
    "paulg": {
        "description": "Paul Graham (Y Combinator)",
        "category": "startups"
    },
    "sama": {
        "description": "Sam Altman (OpenAI)",
        "category": "ai"
    },
    "vitalikbuterin": {
        "description": "Виталик Бутерин (Ethereum)",
        "category": "crypto"
    },
    "naval": {
        "description": "Naval Ravikant",
        "category": "crypto"
    },
    
    # === БЕЗОПАСНОСТЬ ===
    "SwiftOnSecurity": {
        "description": "Swift on Security",
        "category": "security"
    },
    "robertmlee": {
        "description": "Robert M. Lee (Cybersecurity)",
        "category": "security"
    },
}

# ===================== ГОТОВЫЕ НАБОРЫ (PRESETS) =====================

PRESETS = {
    "Начинающий (только Habr)": [
        {"name": "Habr", "url": "https://habr.com/ru/rss/all/", "type": "rss"},
    ],
    
    "Полный (все технологии)": [
        # RSS
        {"name": "Habr", "url": "https://habr.com/ru/rss/all/", "type": "rss"},
        {"name": "Geektimes", "url": "https://geektimes.ru/rss/all/", "type": "rss"},
        {"name": "Opennet", "url": "https://www.opennet.ru/opennews/opennews.rss", "type": "rss"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "type": "rss"},
        # Zen
        {"name": "Zen Технологии", "url": "https://dzen.ru/feed/rss/?channel_name=technologies", "type": "zen"},
        {"name": "Zen ИИ", "url": "https://dzen.ru/feed/rss/?channel_name=artificial_intelligence", "type": "zen"},
        {"name": "Zen Крипто", "url": "https://dzen.ru/feed/rss/?channel_name=crypto_news", "type": "zen"},
        # Twitter
        {"name": "Илон Маск", "url": "elonmusk", "type": "twitter"},
    ],
    
    "Криптовалюты": [
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "type": "rss"},
        {"name": "The Block", "url": "https://www.theblock.co/rss.xml", "type": "rss"},
        {"name": "Zen Крипто", "url": "https://dzen.ru/feed/rss/?channel_name=crypto_news", "type": "zen"},
        {"name": "Виталик Бутерин", "url": "vitalikbuterin", "type": "twitter"},
        {"name": "Naval", "url": "naval", "type": "twitter"},
    ],
    
    "Безопасность": [
        {"name": "Habr Security", "url": "https://habr.com/ru/rss/hubs/information_security/", "type": "rss"},
        {"name": "Zen Cybersecurity", "url": "https://dzen.ru/feed/rss/?channel_name=cybersecurity", "type": "zen"},
        {"name": "Swift on Security", "url": "SwiftOnSecurity", "type": "twitter"},
        {"name": "Robert M. Lee", "url": "robertmlee", "type": "twitter"},
    ],
    
    "Стартапы и инвестиции": [
        {"name": "Habr", "url": "https://habr.com/ru/rss/all/", "type": "rss"},
        {"name": "Zen Стартапы", "url": "https://dzen.ru/feed/rss/?channel_name=startups", "type": "zen"},
        {"name": "Zen Финтех", "url": "https://dzen.ru/feed/rss/?channel_name=fintech", "type": "zen"},
        {"name": "Paul Graham", "url": "paulg", "type": "twitter"},
        {"name": "Sam Altman", "url": "sama", "type": "twitter"},
    ],
}

# ===================== СКРИПТ ДЛЯ ДОБАВЛЕНИЯ ИСТОЧНИКОВ =====================

"""
Использование:

python -c "from config import PRESETS, RSS_FEEDS; 
from news_bot import NewsBot, NewsDatabase

db = NewsDatabase()

# Способ 1: Добавить популярный RSS
for name, feed in RSS_FEEDS.items():
    db.add_source(name, feed['url'], 'rss')
    print(f'✅ Добавлен {name}')

# Способ 2: Использовать готовый preset
preset = PRESETS['Криптовалюты']
for source in preset:
    db.add_source(source['name'], source['url'], source['type'])
    print(f'✅ Добавлен {source[\"name\"]}')
"
"""

# ===================== СОВЕТЫ ПО ВЫБОРУ ИСТОЧНИКОВ =====================

RECOMMENDATIONS = {
    "Для новичков": {
        "sources": ["Habr", "Dev.to"],
        "reason": "Качественный контент, хороший модерейшн",
        "update_freq": "Ежедневно"
    },
    
    "Для криптотрейдеров": {
        "sources": ["CoinDesk", "The Block", "Twitter (Crypto personalities)"],
        "reason": "Оперативность и глубокая аналитика",
        "update_freq": "Каждый час"
    },
    
    "Для специалистов по безопасности": {
        "sources": ["Habr Security Hub", "Twitter Security Researchers"],
        "reason": "Новые уязвимости и методы защиты",
        "update_freq": "Несколько раз в день"
    },
    
    "Для разработчиков": {
        "sources": ["GitHub Blog", "Python.org", "Dev.to", "ArXiv"],
        "reason": "Обновления инструментов и лучшие практики",
        "update_freq": "Ежедневно"
    },
    
    "Для инвесторов": {
        "sources": ["Startups channels", "Fintech channels", "Twitter (VCs)"],
        "reason": "Новые раунды финансирования и тренды",
        "update_freq": "Ежедневно"
    },
}

# ===================== ПРОВЕРКА ИСТОЧНИКОВ =====================

"""
Валидация RSS перед добавлением:

import requests
import feedparser

def validate_rss(url):
    try:
        response = requests.get(url, timeout=5)
        feed = feedparser.parse(response.content)
        
        if feed.bozo:
            print(f"⚠️ RSS может быть некорректным: {feed.bozo_exception}")
        
        if len(feed.entries) > 0:
            print(f"✅ RSS валиден")
            print(f"📰 Название: {feed.feed.title}")
            print(f"📝 Количество статей: {len(feed.entries)}")
            print(f"🔗 Первая статья: {feed.entries[0].title}")
            return True
        else:
            print(f"❌ RSS пуст")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

# Использование:
validate_rss("https://habr.com/ru/rss/all/")
"""

# ===================== ЧАСТО ИСПОЛЬЗУЕМЫЕ КОМБИНАЦИИ =====================

TEMPLATES = """
📌 БЫСТРЫЕ ШАБЛОНЫ ДЛЯ COPY-PASTE

1️⃣ ТОЛЬКО РУССКОЯЗЫЧНОЕ:
   - Habr
   - Geektimes
   - Opennet.ru
   - Zen (any category)

2️⃣ ТЕХНОЛОГИИ + КРИПТОВАЛЮТЫ:
   - Habr
   - CoinDesk
   - GitHub Blog
   - Zen Tech
   - Zen Crypto
   - elonmusk

3️⃣ ИССЛЕДОВАНИЯ И ИИ:
   - ArXiv
   - GitHub Blog
   - Zen AI
   - Sam Altman (Twitter)
   - Paul Graham (Twitter)

4️⃣ МАКСИМАЛЬНО ПОЛНЫЙ НАБОР:
   - Все RSS из категории "tech"
   - Все каналы Дзена
   - Топ 5 Twitter аккаунтов в области

💡 СОВЕТ: Начните с 3-5 источников, постепенно добавляйте новые
         по мере настройки бота.
"""
