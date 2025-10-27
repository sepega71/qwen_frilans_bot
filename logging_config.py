#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для настройки логирования в системе.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_level=logging.INFO, log_file=None, max_bytes=10000000, backup_count=5):
    """
    Настройка логирования для системы.

    Args:
        log_level: Уровень логирования (по умолчанию INFO)
        log_file: Путь к файлу логов (если None, логи будут выводиться только в консоль)
        max_bytes: Максимальный размер файла лога в байтах перед ротацией
        backup_count: Количество архивных файлов логов для хранения
    """
    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Основной логгер системы
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Удаляем все существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Обработчик для консольного вывода
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Обработчик для файлового вывода (если указан путь к файлу)
    if log_file:
        # Создаем директорию для логов, если она не существует
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Обработчик с ротацией файлов
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Дополнительные логгеры для конкретных компонентов системы
    setup_component_loggers(log_level, formatter, log_file, max_bytes, backup_count)


def setup_component_loggers(log_level, formatter, log_file=None, max_bytes=10000000, backup_count=5):
    """
    Настройка логгеров для конкретных компонентов системы.

    Args:
        log_level: Уровень логирования
        formatter: Форматтер для логов
        log_file: Путь к файлу логов
        max_bytes: Максимальный размер файла лога в байтах перед ротацией
        backup_count: Количество архивных файлов логов для хранения
    """
    # Логгер для ядра бота
    bot_logger = logging.getLogger('bot_core')
    bot_logger.setLevel(log_level)
    
    # Логгер для модуля сбора данных
    collector_logger = logging.getLogger('data_collector')
    collector_logger.setLevel(log_level)
    
    # Логгер для системы фильтрации
    filter_logger = logging.getLogger('filter_engine')
    filter_logger.setLevel(log_level)
    
    # Логгер для системы персонализации
    personalization_logger = logging.getLogger('personalization_engine')
    personalization_logger.setLevel(log_level)
    
    # Логгер для системы уведомлений
    notification_logger = logging.getLogger('notification_engine')
    notification_logger.setLevel(log_level)
    
    # Логгер для планировщика уведомлений
    scheduler_logger = logging.getLogger('notification_scheduler')
    scheduler_logger.setLevel(log_level)
    
    # Логгер для хранилища данных
    storage_logger = logging.getLogger('data_storage')
    storage_logger.setLevel(log_level)
    
    # Логгер для менеджера настроек пользователей
    settings_logger = logging.getLogger('user_settings_manager')
    settings_logger.setLevel(log_level)
    
    # Логгер для трекера взаимодействия с пользователем
    interaction_logger = logging.getLogger('user_interaction_tracker')
    interaction_logger.setLevel(log_level)
    
    # Логгер для источников данных
    fl_ru_logger = logging.getLogger('data_sources.fl_ru')
    fl_ru_logger.setLevel(log_level)
    
    weblancer_logger = logging.getLogger('data_sources.weblancer')
    weblancer_logger.setLevel(log_level)
    
    freemarket_logger = logging.getLogger('data_sources.freemarket')
    freemarket_logger.setLevel(log_level)
    
    github_logger = logging.getLogger('data_sources.github')
    github_logger.setLevel(log_level)
    
    telegram_logger = logging.getLogger('data_sources.telegram')
    telegram_logger.setLevel(log_level)

    # Если указан файл логов, добавляем файловые обработчики для компонентов
    if log_file:
        # Создаем директорию для логов, если она не существует
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Обработчики с ротацией файлов для каждого компонента
        components = [
            ('bot_core', bot_logger),
            ('data_collector', collector_logger),
            ('filter_engine', filter_logger),
            ('personalization_engine', personalization_logger),
            ('notification_engine', notification_logger),
            ('notification_scheduler', scheduler_logger),
            ('data_storage', storage_logger),
            ('user_settings_manager', settings_logger),
            ('user_interaction_tracker', interaction_logger),
            ('data_sources.fl_ru', fl_ru_logger),
            ('data_sources.weblancer', weblancer_logger),
            ('data_sources.freemarket', freemarket_logger),
            ('data_sources.github', github_logger),
            ('data_sources.telegram', telegram_logger),
        ]

        for component_name, logger in components:
            component_log_file = log_file.replace('.log', f'_{component_name}.log')
            file_handler = logging.handlers.RotatingFileHandler(
                component_log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)


def get_logger(component_name):
    """
    Получение логгера для конкретного компонента системы.

    Args:
        component_name: Название компонента (например, 'bot_core', 'data_collector')

    Returns:
        logging.Logger: Логгер для указанного компонента
    """
    return logging.getLogger(component_name)


# Примеры использования:
if __name__ == "__main__":
    # Настройка логирования в файл и консоль
    setup_logging(
        log_level=logging.INFO,
        log_file="logs/frilans_bot.log",
        max_bytes=10000000,  # 10MB
        backup_count=5
    )

    # Пример использования логгера в компоненте
    logger = get_logger('bot_core')
    logger.info("Система запущена")
    logger.debug("Отладочное сообщение")
    logger.warning("Предупреждение")
    logger.error("Сообщение об ошибке")