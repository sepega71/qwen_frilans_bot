# Руководство по установке и запуску телеграм-бота для фрилансеров

## Общая информация

Телеграм-бот для фрилансеров автоматически собирает, фильтрует и персонализированно рассылает актуальные заказы и вакансии из различных источников. Система использует только бесплатные, открытые и легальные источники, доступные в России.

## Системные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git (для клонирования репозитория)
- Telegram Bot Token (получается у @BotFather в Telegram)

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ваш-аккаунт/ваш-репозиторий.git
cd ваш-репозиторий
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate  # На Linux/Mac
# или
venv\Scripts\activate  # На Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

Если файл `requirements.txt` отсутствует, установите следующие пакеты:

```bash
pip install python-telegram-bot aiohttp requests beautifulsoup4 telethon
```

## Конфигурация

### 1. Получение Telegram Bot Token

1. Откройте Telegram и найдите @BotFather
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания нового бота
4. Скопируйте предоставленный токен

### 2. Настройка Telegram API (для мониторинга Telegram-каналов)

Если вы хотите использовать функциональность мониторинга Telegram-каналов:

1. Перейдите на https://my.telegram.org
2. Войдите в систему с вашим номером телефона
3. Создайте новое приложение
4. Запишите `api_id` и `api_hash`

### 3. Создание конфигурационного файла

Создайте файл `config.py` в корне проекта:

```python
# config.py
TELEGRAM_BOT_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
TELEGRAM_API_ID = "ВАШ_API_ID"  # Необязательно
TELEGRAM_API_HASH = "ВАШ_API_HASH"  # Необязательно
TELEGRAM_PHONE = "ВАШ_НОМЕР_ТЕЛЕФОНА"  # Необязательно, формат: "+71234567890"

# Настройки базы данных
DATABASE_PATH = "frilans_bot.db"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FILE = "frilans_bot.log"
```

## Запуск бота

### 1. Запуск в режиме разработки

```bash
python bot_core.py
```

### 2. Запуск с использованием скрипта запуска

Создайте скрипт запуска `run_bot.py`:

```python
# run_bot.py
import asyncio
from bot_core import setup_bot_application
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE

async def main():
    # Инициализация бота с учетными данными
    bot = setup_bot_application(
        token=TELEGRAM_BOT_TOKEN,
        telegram_api_id=TELEGRAM_API_ID if 'TELEGRAM_API_ID' in globals() else None,
        telegram_api_hash=TELEGRAM_API_HASH if 'TELEGRAM_API_HASH' in globals() else None,
        telegram_phone=TELEGRAM_PHONE if 'TELEGRAM_PHONE' in globals() else None
    )
    
    # Запуск бота
    bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

Затем запустите:

```bash
python run_bot.py
```

## Использование

### Команды бота

- `/start` - начать работу с ботом
- `/help` - справка по использованию
- `/settings` - настройка профиля и предпочтений
- `/filter` - настройка фильтров поиска
- `/subscribe` - подписаться на рассылку
- `/unsubscribe` - отписаться от рассылки
- `/add_keywords` - добавить ключевые слова
- `/remove_keywords` - удалить ключевые слова
- `/add_tech` - добавить технологии
- `/remove_tech` - удалить технологии
- `/set_budget` - установить бюджет
- `/set_region` - установить регион
- `/set_project_type` - установить тип проекта
- `/set_experience` - установить уровень опыта
- `/set_payment_type` - установить форму оплаты

### Примеры использования

#### Настройка фильтров

1. Добавление ключевых слов:
   ```
   /add_keywords python, telegram, bot
   ```

2. Установка бюджета:
   ```
   /set_budget 10000 50000
   ```

3. Установка региона:
   ```
   /set_region Москва, Санкт-Петербург
   ```

#### Подписка на рассылку

1. Настройте фильтры
2. Используйте команду `/subscribe`

## Возможные проблемы и решения

### Ошибка при запуске: "ModuleNotFoundError"

Убедитесь, что все зависимости установлены:

```bash
pip install -r requirements.txt
```

### Бот не отвечает

Проверьте, что токен бота указан правильно и бот активен.

### Ошибка при доступе к Telegram API

Убедитесь, что `api_id` и `api_hash` указаны правильно, и номер телефона подтвержден.

## Обновление бота

1. Остановите работающий бот (Ctrl+C)
2. Обновите код из репозитория:

```bash
git pull origin main
```

3. При необходимости обновите зависимости:

```bash
pip install -r requirements.txt --upgrade
```

4. Запустите бота снова:

```bash
python run_bot.py
```

## Заключение

Поздравляем! Вы успешно установили и запустили телеграм-бота для фрилансеров. Бот будет автоматически собирать, фильтровать и отправлять актуальные заказы и вакансии в соответствии с настройками пользователей.