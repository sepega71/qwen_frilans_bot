#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки работы с настройками пользователя
"""

from user_settings_manager import UserSettingsManager, UserSettings, UserFilters


def test_user_settings():
    """Тест создания и работы с настройками пользователя"""
    print("Тест создания и работы с настройками пользователя...")
    
    # Создание менеджера настроек
    manager = UserSettingsManager("test_user_settings.json")
    
    # Получение настроек пользователя
    user_id = 123456789
    settings = manager.get_user_settings(user_id)
    
    print(f"Тип settings: {type(settings)}")
    print(f"Тип settings.filters: {type(settings.filters)}")
    
    # Проверка, что filters является объектом UserFilters
    if isinstance(settings.filters, UserFilters):
        print("✓ settings.filters является объектом UserFilters")
    else:
        print("✗ settings.filters НЕ является объектом UserFilters")
        print(f"  Тип: {type(settings.filters)}")
        print(f"  Значение: {settings.filters}")
    
    # Проверка доступа к атрибутам
    try:
        keywords = settings.filters.keywords
        print(f"✓ Доступ к keywords: {keywords}")
    except Exception as e:
        print(f"✗ Ошибка при доступе к keywords: {e}")
    
    try:
        technologies = settings.filters.technologies
        print(f"✓ Доступ к technologies: {technologies}")
    except Exception as e:
        print(f"✗ Ошибка при доступе к technologies: {e}")
    
    try:
        budget_min = settings.filters.budget_min
        print(f"✓ Доступ к budget_min: {budget_min}")
    except Exception as e:
        print(f"✗ Ошибка при доступе к budget_min: {e}")
    
    # Проверка методов
    try:
        manager.add_keywords(user_id, ["python", "telegram"])
        print("✓ Метод add_keywords работает")
    except Exception as e:
        print(f"✗ Ошибка в методе add_keywords: {e}")
    
    try:
        manager.remove_keywords(user_id, ["python"])
        print("✓ Метод remove_keywords работает")
    except Exception as e:
        print(f"✗ Ошибка в методе remove_keywords: {e}")


if __name__ == "__main__":
    test_user_settings()