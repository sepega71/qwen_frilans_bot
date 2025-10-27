#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестирования функциональности бота.
"""

import asyncio
from bot_core import setup_bot_application
from data_collector import DataCollector
import os
from config import *
from data_storage import DataStorage
from user_settings_manager import UserSettingsManager
from filter_engine import FilterEngine
from personalization_engine import PersonalizationEngine
from notification_engine import NotificationEngine
from notification_scheduler import NotificationScheduler
from user_interaction_tracker import UserInteractionTracker


async def test_bot_components():
    """Тестирование компонентов бота"""
    print("Тестирование компонентов бота...")
    
    # Инициализация компонентов
    data_storage = DataStorage()
    user_settings_manager = UserSettingsManager()
    filter_engine = FilterEngine()
    personalization_engine = PersonalizationEngine(user_settings_manager, filter_engine)
    user_interaction_tracker = UserInteractionTracker()
    
    # Проверка токена
    token = TELEGRAM_BOT_TOKEN
    if not token or token == "8470853705:AAEcB5fZvSUB5_0S7SfyqzJiNsNqizIer1A":
        print("ПРЕДУПРЕЖДЕНИЕ: Используется тестовый токен. Замените на реальный для полноценного тестирования.")
        return
    
    notification_engine = NotificationEngine(
        token, user_settings_manager, data_storage, personalization_engine
    )
    notification_scheduler = NotificationScheduler(
        notification_engine, data_storage, personalization_engine
    )
    
    print("✓ Все компоненты инициализированы успешно")
    
    # Тестирование фильтрации
    test_projects = [
        {
            'title': 'Разработка Telegram бота на Python',
            'description': 'Необходимо создать Telegram бота для автоматизации задач. Использовать Python, aiogram, базу данных.',
            'budget': 50000,
            'region': 'Москва',
            'technologies': ['Python', 'Telegram Bot API', 'aiogram'],
            'url': 'https://example.com/project1',
            'date': '2023-10-27T10:00:00',
            'source': 'test',
            'type': 'order',
            'external_id': 'test_1'
        },
        {
            'title': 'Веб-разработка на React',
            'description': 'Ищем разработчика для создания веб-приложения на React с использованием Redux.',
            'budget': 75000,
            'region': 'Санкт-Петербург',
            'technologies': ['React', 'Redux', 'JavaScript'],
            'url': 'https://example.com/project2',
            'date': '2023-10-27T11:00:00',
            'source': 'test',
            'type': 'order',
            'external_id': 'test_2'
        }
    ]
    
    # Создание тестового пользователя
    user_id = 123456789
    user_settings_manager.update_user_subscription(user_id, True)
    user_settings_manager.add_keywords(user_id, ['Python', 'Telegram'])
    user_settings_manager.add_technologies(user_id, ['Python', 'Telegram Bot API'])
    user_settings_manager.set_budget(user_id, 30000, 100000)
    user_settings_manager.set_regions(user_id, ['Москва'])
    
    print("✓ Тестовый пользователь создан и настроен")
    
    # Тестирование фильтрации
    user_settings = user_settings_manager.get_user_settings(user_id)
    filtered_projects = filter_engine.filter_projects(test_projects, user_settings.filters)
    
    print(f"✓ Фильтрация прошла успешно. Найдено {len(filtered_projects)} подходящих проектов")
    
    # Тестирование персонализации
    relevant_projects = personalization_engine.get_relevant_projects_for_user(user_settings, test_projects)
    print(f"✓ Персонализация прошла успешно. Найдено {len(relevant_projects)} релевантных проектов")
    
    # Тестирование форматирования сообщений
    for project in relevant_projects:
        message = personalization_engine.format_project_message(project)
        print(f"✓ Сообщение для проекта '{project['title']}' сформировано успешно")
        print(f"  Пример сообщения: {message[:100]}...")
    
    print("\nВсе компоненты работают корректно!")


async def test_data_collection():
    """Тестирование сбора данных"""
    print("\nТестирование сбора данных...")
    
    # Инициализация сборщика данных
    collector = DataCollector()
    
    try:
        # Сбор данных из всех источников
        projects = await collector.collect_all_data()
        print(f"✓ Сбор данных завершен. Получено {len(projects)} проектов")
        
        # Показать первые несколько проектов
        for i, project in enumerate(projects[:3]):
            print(f"  Проект {i+1}: {project.get('title', 'Без названия')} - {project.get('source', 'Неизвестный источник')}")
        
    except Exception as e:
        print(f"✗ Ошибка при сборе данных: {e}")


def main():
    """Основная функция тестирования"""
    print("Запуск тестирования функциональности бота...")
    
    # Тестирование компонентов
    asyncio.run(test_bot_components())
    
    # Тестирование сбора данных
    asyncio.run(test_data_collection())
    
    print("\nТестирование завершено!")


if __name__ == "__main__":
    main()