# Инструкции по конфигурации телеграм-бота для фрилансеров

## Общая информация

Данный документ описывает процесс конфигурации телеграм-бота для фрилансеров. Конфигурация включает в себя настройку основных параметров системы, параметров подключения к внешним источникам данных, а также настройку параметров безопасности и соответствия требованиям законодательства РФ.

## Структура конфигурации

Конфигурация системы организована в несколько уровней:

1. **Основная конфигурация** - основные параметры системы, такие как токены, пути к базе данных и т.д.
2. **Конфигурация источников данных** - параметры подключения к различным источникам (fl.ru, weblancer.net и др.)
3. **Конфигурация безопасности** - параметры, связанные с безопасностью и конфиденциальностью
4. **Конфигурация уведомлений** - параметры планирования и отправки уведомлений

## Основная конфигурация

### Файл конфигурации

Создайте файл `config.py` в корне проекта со следующей структурой:

```python
# config.py

# Основные настройки
TELEGRAM_BOT_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
DATABASE_PATH = "frilans_bot.db"
LOG_LEVEL = "INFO"
LOG_FILE = "frilans_bot.log"

# Настройки Telegram API (для мониторинга Telegram-каналов)
TELEGRAM_API_ID = "ВАШ_API_ID"  # Необязательно
TELEGRAM_API_HASH = "ВАШ_API_HASH"  # Необязательно
TELEGRAM_PHONE = "ВАШ_НОМЕР_ТЕЛЕФОНА"  # Необязательно, формат: "+71234567890"

# Настройки GitHub API (для доступа к GitHub)
GITHUB_TOKEN = "ВАШ_GITHUB_TOKEN"  # Необязательно, но рекомендуется

# Настройки системы
SYSTEM_CONFIG = {
    'check_interval_minutes': 60,  # Интервал проверки новых проектов
    'max_projects_per_notification': 5,  # Максимальное количество проектов в одном уведомлении
    'data_retention_days': 30,  # Срок хранения данных в днях
    'enable_auditing': True,  # Включить аудит действий
    'max_log_size_mb': 10,  # Максимальный размер файла лога в МБ
    'max_log_files': 5,  # Максимальное количество файлов логов
}
```

### Параметры основной конфигурации

- `TELEGRAM_BOT_TOKEN` - токен вашего Telegram бота, полученный от @BotFather
- `DATABASE_PATH` - путь к файлу базы данных SQLite
- `LOG_LEVEL` - уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE` - путь к файлу лога
- `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_PHONE` - учетные данные для доступа к Telegram API (требуются для мониторинга Telegram-каналов)
- `GITHUB_TOKEN` - токен для доступа к GitHub API (рекомендуется для увеличения лимитов запросов)
- `SYSTEM_CONFIG` - словарь с дополнительными настройками системы:
  - `check_interval_minutes` - интервал проверки новых проектов в минутах
  - `max_projects_per_notification` - максимальное количество проектов в одном уведомлении
  - `data_retention_days` - срок хранения данных в днях
  - `enable_auditing` - включить аудит действий
  - `max_log_size_mb` - максимальный размер файла лога в МБ
  - `max_log_files` - максимальное количество файлов логов

## Конфигурация источников данных

### fl.ru

Для доступа к fl.ru используются RSS-лента и веб-скрапинг. Дополнительная конфигурация не требуется.

### weblancer.net

Для доступа к weblancer.net используются RSS-лента и веб-скрапинг. Дополнительная конфигурация не требуется.

### freemarket.ru

Для доступа к freemarket.ru используется веб-скрапинг. Дополнительная конфигурация не требуется.

### GitHub

Для доступа к GitHub API рекомендуется использовать токен, который указывается в параметре `GITHUB_TOKEN` в основной конфигурации.

### Telegram-каналы

Для мониторинга Telegram-каналов требуются следующие параметры:

- `TELEGRAM_API_ID` - API ID приложения Telegram
- `TELEGRAM_API_HASH` - API Hash приложения Telegram
- `TELEGRAM_PHONE` - номер телефона для аутентификации

Для получения этих параметров:

1. Перейдите на https://my.telegram.org
2. Войдите в систему с вашим номером телефона
3. Создайте новое приложение
4. Запишите `api_id` и `api_hash`

## Конфигурация безопасности

### Хранение конфиденциальных данных

Все конфиденциальные данные (токены, учетные данные) должны храниться в защищенном файле конфигурации (`config.py`), который не должен быть добавлен в систему контроля версий.

Рекомендуется использовать переменные окружения для хранения чувствительных данных:

```python
import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
```

### Шифрование данных

Система должна использовать шифрование для хранения конфиденциальных данных. В текущей реализации данные пользователей (включая фильтры) хранятся в SQLite базе данных в открытом виде. Для усиления безопасности рекомендуется:

1. Использовать шифрованную базу данных
2. Шифровать чувствительные поля в базе данных
3. Обеспечить безопасный доступ к файлам базы данных

### Аудит и логирование

Система поддерживает аудит действий пользователей и системных событий. Для включения аудита установите параметр `enable_auditing` в значение `True` в конфигурации.

## Конфигурация уведомлений

### Планирование уведомлений

Система поддерживает два типа уведомлений:

1. **Мгновенные уведомления** - отправляются сразу при появлении новых проектов, соответствующих фильтрам пользователя
2. **Ежедневный дайджест** - отправляется один раз в день в заданное время

Для настройки времени ежедневного дайджеста используйте метод `set_daily_notification_time` в планировщике уведомлений:

```python
from notification_scheduler import NotificationScheduler

scheduler = NotificationScheduler(notification_engine, data_storage, personalization_engine)
scheduler.set_daily_notification_time(hour=10, minute=0)  # Установить время на 10:00
```

### Частота проверки новых проектов

Частота проверки новых проектов определяется параметром `check_interval_minutes` в системной конфигурации. Рекомендуется устанавливать значение не менее 30 минут, чтобы избежать частых запросов к источникам данных.

## Пример полного файла конфигурации

```python
# config.py

import os

# Основные настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'ВАШ_TELEGRAM_BOT_TOKEN')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'frilans_bot.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'frilans_bot.log')

# Настройки Telegram API (для мониторинга Telegram-каналов)
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')

# Настройки GitHub API (для доступа к GitHub)
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Настройки системы
SYSTEM_CONFIG = {
    'check_interval_minutes': int(os.getenv('CHECK_INTERVAL_MINUTES', '60')),
    'max_projects_per_notification': int(os.getenv('MAX_PROJECTS_PER_NOTIFICATION', '5')),
    'data_retention_days': int(os.getenv('DATA_RETENTION_DAYS', '30')),
    'enable_auditing': os.getenv('ENABLE_AUDITING', 'True').lower() == 'true',
    'max_log_size_mb': int(os.getenv('MAX_LOG_SIZE_MB', '10')),
    'max_log_files': int(os.getenv('MAX_LOG_FILES', '5')),
}
```

## Запуск с использованием конфигурации

Для использования конфигурации в коде создайте файл `run_bot.py`:

```python
# run_bot.py
import asyncio
from bot_core import setup_bot_application
from config import (
    TELEGRAM_BOT_TOKEN, 
    TELEGRAM_API_ID, 
    TELEGRAM_API_HASH, 
    TELEGRAM_PHONE,
    GITHUB_TOKEN,
    SYSTEM_CONFIG
)
from management_module import ManagementModule

async def main():
    # Инициализация модуля управления для загрузки конфигурации
    management_module = ManagementModule()
    
    # Обновление конфигурации из файла
    management_module.update_config(**SYSTEM_CONFIG)
    
    # Инициализация бота с учетными данными
    bot = setup_bot_application(
        token=TELEGRAM_BOT_TOKEN,
        telegram_api_id=TELEGRAM_API_ID,
        telegram_api_hash=TELEGRAM_API_HASH,
        telegram_phone=TELEGRAM_PHONE,
        github_token=GITHUB_TOKEN
    )
    
    # Запуск бота
    bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Заключение

Правильная конфигурация системы является важным шагом для обеспечения стабильной и безопасной работы телеграм-бота. Следуйте рекомендациям, изложенным в этом документе, для настройки системы в соответствии с вашими требованиями и условиями эксплуатации.