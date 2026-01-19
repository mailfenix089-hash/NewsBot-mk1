# Развертывание Telegram News Bot на Linux сервере (Ubuntu/Debian)

## 🖥️ Вариант 1: Простой запуск с systemd (рекомендуется)

### Шаг 1: Подготовка сервера

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить зависимости Python
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Создать пользователя для бота
sudo useradd -m -s /bin/bash newsbot
sudo su - newsbot
```

### Шаг 2: Клонирование и настройка

```bash
# Создать директорию проекта
mkdir -p /home/newsbot/telegram-news-bot
cd /home/newsbot/telegram-news-bot

# Скопировать файлы
# (или клонировать из Git репозитория)
# git clone <repository_url> .

# Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install aiogram feedparser aiohttp python-dotenv apscheduler
```

### Шаг 3: Конфигурация

```bash
# Создать .env файл
nano .env
```

Вставьте (Ctrl+Shift+V или правый клик):

```env
TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
ADMIN_ID=YOUR_ADMIN_ID
TELEGRAM_CHANNELS=[-1001234567890]
```

Сохраните: **Ctrl+X → Y → Enter**

### Шаг 4: Тестирование

```bash
# Запустить бот для проверки
python news_bot.py
```

Если видите `🚀 Бот запущен!` - отлично!

**Ctrl+C** для остановки

### Шаг 5: Создание systemd сервиса

```bash
# Выход из виртуального окружения
deactivate
exit

# Создать systemd файл
sudo nano /etc/systemd/system/newsbot.service
```

Вставьте:

```ini
[Unit]
Description=Telegram News Bot
After=network.target

[Service]
User=newsbot
WorkingDirectory=/home/newsbot/telegram-news-bot
ExecStart=/home/newsbot/telegram-news-bot/venv/bin/python news_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Сохраните: **Ctrl+X → Y → Enter**

### Шаг 6: Запуск сервиса

```bash
# Перезагрузить systemd
sudo systemctl daemon-reload

# Запустить сервис
sudo systemctl start newsbot

# Включить автозапуск при перезагрузке
sudo systemctl enable newsbot

# Проверить статус
sudo systemctl status newsbot

# Просмотр логов
sudo journalctl -u newsbot -f
```

---

## 🐳 Вариант 2: Docker (для контейнеризации)

### Создание Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить системные зависимости
RUN apt-get update && apt-get install -y \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Копировать requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копировать исходный код
COPY news_bot.py .
COPY advanced_bot.py .

# Запустить бота
CMD ["python", "news_bot.py"]
```

### Создание requirements.txt

```
aiogram==3.5.0
feedparser==6.0.10
aiohttp==3.9.3
python-dotenv==1.0.1
apscheduler==3.11.0
```

### Сборка и запуск

```bash
# Сборка образа
docker build -t telegram-news-bot .

# Запуск контейнера
docker run -d \
  --name newsbot \
  --env-file .env \
  -v /path/to/data:/app/data \
  telegram-news-bot

# Просмотр логов
docker logs -f newsbot

# Остановка
docker stop newsbot
docker rm newsbot
```

### Docker Compose (несколько сервисов)

```yaml
version: '3.8'

services:
  newsbot:
    build: .
    container_name: telegram-news-bot
    env_file: .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Запуск:
```bash
docker-compose up -d
docker-compose logs -f
```

---

## ☁️ Вариант 3: Облако (Render, Railway, Heroku)

### Railway.app (простейший вариант)

1. **Регистрация**: https://railway.app
2. **Создать проект** → Choose Template → Python
3. **Загрузить на GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/telegram-news-bot
   git push -u origin main
   ```

4. **В Railway**: Connect GitHub репозиторий
5. **Добавить переменные окружения**:
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_ID`
   - `TELEGRAM_CHANNELS`

6. **Запуск**: Railway автоматически запустит на основе Procfile

### Procfile (для облачных платформ)

```
worker: python news_bot.py
```

---

## 📊 Мониторинг и поддержка

### Просмотр логов

```bash
# systemd
sudo journalctl -u newsbot -f
sudo journalctl -u newsbot --since "2 hours ago"

# Docker
docker logs -f newsbot
docker logs --tail 100 newsbot

# Из самого сервера (если используется logging в файл)
tail -f /var/log/newsbot.log
```

### Проверка статуса

```bash
# Процесс запущен?
ps aux | grep news_bot

# Занимаемая память
free -h

# Дисковое пространство (для БД)
df -h

# Открытые порты
netstat -tulnp | grep python
```

### Перезагрузка

```bash
# systemd
sudo systemctl restart newsbot

# Docker
docker restart newsbot
```

---

## 🔧 Настройка Nginx (опционально, если API)

Если вы расширите бот и создадите REST API:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🚨 Полезные команды

```bash
# Получить статус всех сервисов
sudo systemctl status

# Перезагрузить сервер (потребуется sudo)
sudo reboot

# Остановить бот навсегда
sudo systemctl stop newsbot
sudo systemctl disable newsbot

# Полностью удалить сервис
sudo rm /etc/systemd/system/newsbot.service
sudo systemctl daemon-reload

# Посмотреть размер БД
ls -lh /home/newsbot/telegram-news-bot/news_bot.db

# Зарезервировать БД
cp /home/newsbot/telegram-news-bot/news_bot.db \
   /home/newsbot/telegram-news-bot/news_bot.db.backup.$(date +%Y%m%d)
```

---

## ✅ Checklist для продакшена

- [ ] Токен бота прав и работает
- [ ] ADMIN_ID установлен правильно
- [ ] ID каналов в JSON формате: `[-1001234567890]`
- [ ] Минимум 1 источник добавлен и протестирован
- [ ] Сервис запускается автоматически после перезагрузки
- [ ] Логи собираются и их можно просмотреть
- [ ] БД бэкапится регулярно
- [ ] Настроены уведомления об ошибках (опционально)
- [ ] Проверена работа при перезагрузке сервера

---

## 🆘 Troubleshooting

| Проблема | Решение |
|----------|---------|
| Bot не запускается | Проверьте логи: `journalctl -u newsbot` |
| ModuleNotFoundError | Убедитесь, что виртуальное окружение активировано |
| Connection refused | Проверьте интернет соединение, firewall |
| Bot не постит новости | Используйте `/fetch` для отладки |
| Out of memory | Увеличьте RAM сервера или используйте Redis для кэша |

---

## 📞 Контакты поддержки

- GitHub Issues: [Создать issue](https://github.com/issues)
- Telegram: [@BotFather](https://t.me/botfather) - для помощи с токенами
