#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки работы FilterEngine
"""

from filter_engine import FilterEngine
from user_settings_manager import UserSettingsManager, UserSettings, UserFilters


def test_filter_engine():
    """Тест работы FilterEngine"""
    print("Тест работы FilterEngine...")
    
    # Создание менеджера настроек
    manager = UserSettingsManager("test_user_settings.json")
    
    # Получение настроек пользователя
    user_id = 123456789
    settings = manager.get_user_settings(user_id)
    
    # Добавление ключевых слов
    manager.add_keywords(user_id, ["python", "telegram"])
    
    # Создание движка фильтрации
    filter_engine = FilterEngine()
    
    # Тестовые проекты
    test_projects = [
        {
            "title": "Разработка Telegram бота на Python",
            "description": "Требуется разработать Telegram бота с использованием Python и библиотеки python-telegram-bot",
            "technologies": ["Python", "Telegram Bot API"],
            "budget": 50000,
            "region": "Удаленная работа",
            "type": "order",
            "source": "fl.ru"
        },
        {
            "title": "Веб-разработка на React",
            "description": "Создание веб-приложения на React с использованием Redux",
            "technologies": ["React", "Redux", "JavaScript"],
            "budget": 75000,
            "region": "Москва",
            "type": "order",
            "source": "weblancer.net"
        }
    ]
    
    print(f"Тип settings.filters: {type(settings.filters)}")
    print(f"Ключевые слова в фильтрах: {settings.filters.keywords}")
    
    # Попытка фильтрации
    try:
        filtered_projects = filter_engine.filter_projects(test_projects, settings.filters)
        print(f"✓ Фильтрация прошла успешно. Найдено проектов: {len(filtered_projects)}")
        
        for i, project in enumerate(filtered_projects):
            print(f"  Проект {i+1}: {project['title']}")
    except Exception as e:
        print(f"✗ Ошибка при фильтрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_filter_engine()