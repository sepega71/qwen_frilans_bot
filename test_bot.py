#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование функционала бота
"""

import asyncio
from data_collector import DataCollector
from config import TELEGRAM_BOT_TOKEN


async def test_data_collection():
    """Тестирование сбора данных"""
    print("Тестирование сбора данных...")
    
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
    print("Запуск тестирования функционала бота...")
    print(f"Токен бота установлен: {'Да' if TELEGRAM_BOT_TOKEN else 'Нет'}")
    
    # Тестирование сбора данных
    asyncio.run(test_data_collection())
    
    print("\nТестирование завершено!")


if __name__ == "__main__":
    main()