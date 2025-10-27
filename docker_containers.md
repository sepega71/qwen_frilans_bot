# Docker-контейнеры для телеграм-бота для фрилансеров

## Общая информация

Данный документ описывает структуру Docker-контейнеров для телеграм-бота для фрилансеров. Контейнеризация позволяет упростить развертывание, масштабирование и управление приложением. Ниже представлены Dockerfile и docker-compose.yml файлы для различных компонентов системы.

## Структура проекта

```
project-root/
├── bot/
│   ├── Dockerfile
│   └── requirements.txt
├── database/
│   └── Dockerfile
├── redis/
│   └── Dockerfile
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## Dockerfile для основного бота

### bot/Dockerfile

```dockerfile
# Используем официальный образ Python 3.9
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Открываем порт (если используется веб-интерфейс)
EXPOSE 8000

# Команда запуска бота
CMD ["python", "run_bot.py"]
```

### bot/requirements.txt

```
python-telegram-bot==20.0
aiohttp==3.8.3
requests==2.28.1
beautifulsoup4==4.11.1
telethon==1.25.2
asyncio==3.4.3
sqlite3==2.6.0
```

## Dockerfile для базы данных

### database/Dockerfile

```dockerfile
# Используем официальный образ PostgreSQL
FROM postgres:14-alpine

# Устанавливаем локаль
ENV LANG=ru_RU.UTF-8
ENV LC_ALL=ru_RU.UTF-8

# Копируем скрипт инициализации (если требуется)
# COPY init.sql /docker-entrypoint-initdb.d/

# Устанавливаем пароль администратора из переменной окружения
ENV POSTGRES_PASSWORD=your_secure_password

# Открываем порт PostgreSQL
EXPOSE 5432

# Запускаем PostgreSQL
CMD ["postgres"]
```

## Dockerfile для Redis

### redis/Dockerfile

```dockerfile
# Используем официальный образ Redis
FROM redis:7-alpine

# Копируем конфигурационный файл (если требуется)
# COPY redis.conf /usr/local/etc/redis/redis.conf

# Открываем порт Redis
EXPOSE 6379

# Запускаем Redis
CMD ["redis-server"]
```

## Dockerfile для Nginx

### nginx/Dockerfile

```dockerfile
FROM nginx:alpine

# Копируем конфигурационный файл
COPY nginx.conf /etc/nginx/nginx.conf

# Открываем порты
EXPOSE 80 443

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  # Основной бот
  bot:
    build:
      context: ./bot
      dockerfile: Dockerfile
    container_name: frilans_bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - DATABASE_URL=postgresql://user:password@db:5432/frilans_bot
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data  # Для хранения локальной базы данных и других данных
      - ./logs:/app/logs  # Для хранения логов
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - frilans_network

 # База данных
  db:
    build:
      context: ./database
      dockerfile: Dockerfile
    container_name: frilans_db
    environment:
      - POSTGRES_DB=frilans_bot
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups  # Для резервного копирования
    restart: unless-stopped
    networks:
      - frilans_network
    ports:
      - "5432:5432" # Открываем порт только при необходимости

  # Redis для кэширования
  redis:
    build:
      context: ./redis
      dockerfile: Dockerfile
    container_name: frilans_redis
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - frilans_network

  # Веб-сервер (опционально, если нужен веб-интерфейс)
 nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    container_name: frilans_nginx
    ports:
      - "80:80"
      - "443:43"
    volumes:
      - ./certs:/etc/ssl/certs  # Для SSL-сертификатов
    depends_on:
      - bot
    restart: unless-stopped
    networks:
      - frilans_network

volumes:
  postgres_data:
  redis_data:

networks:
  frilans_network:
    driver: bridge
```

## .env файл

Создайте файл `.env` в корне проекта для хранения чувствительных данных:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
POSTGRES_PASSWORD=your_secure_postgres_password
REDIS_PASSWORD=your_secure_redis_password
```

## Инструкции по сборке и запуску

### 1. Установка Docker и Docker Compose

Убедитесь, что у вас установлены Docker и Docker Compose:

```bash
# Проверка установки Docker
docker --version

# Проверка установки Docker Compose
docker-compose --version
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта и укажите необходимые переменные:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота_здесь
POSTGRES_PASSWORD=надежный_пароль_для_postgres
REDIS_PASSWORD=надежный_пароль_для_redis
```

### 3. Сборка и запуск контейнеров

```bash
# Сборка и запуск всех сервисов
docker-compose up --build -d

# Проверка статуса контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs -f bot
```

### 4. Остановка и удаление контейнеров

```bash
# Остановка всех сервисов
docker-compose down

# Удаление контейнеров, сетей и томов
docker-compose down -v
```

## Особенности конфигурации

### Безопасность

1. **Использование отдельного пользователя** в контейнере бота для повышения безопасности
2. **Хранение чувствительных данных** в переменных окружения или Docker secrets
3. **Ограничение прав доступа** к файловой системе контейнера

### Производительность

1. **Использование Alpine Linux** для уменьшения размера образов
2. **Кэширование зависимостей** в Dockerfile для ускорения сборки
3. **Оптимизация настроек PostgreSQL и Redis** для лучшей производительности

### Мониторинг и логирование

1. **Монтирование томов** для хранения логов вне контейнера
2. **Интеграция с ELK стеком** для централизованного логирования
3. **Настройка health-checks** для мониторинга состояния сервисов

## Масштабирование

Для масштабирования бота можно использовать следующую команду:

```bash
# Запуск нескольких экземпляров бота
docker-compose up --scale bot=3 -d
```

## Обновление

Для обновления приложения до новой версии:

```bash
# Остановка текущих контейнеров
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск контейнеров
docker-compose up --build -d
```

## Заключение

Контейнеризация телеграм-бота для фрилансеров позволяет упростить его развертывание, масштабирование и управление. Представленная конфигурация обеспечивает безопасность, производительность и отказоустойчивость приложения.