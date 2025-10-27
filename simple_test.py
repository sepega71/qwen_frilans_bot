#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки работы системы сбора данных
"""

import asyncio
from src.data_sources.fl_ru_collector import FlRuCollector


async def test_fl_ru():
    """Тестирование сбора данных с fl.ru"""
    print("Тестирование сбора данных с fl.ru...")
    
    collector = FlRuCollector()
    
    try:
        # Сбор данных с fl.ru через RSS
        async with collector as col:
            projects = await col.fetch_projects_rss()
            print(f"✓ Сбор данных с fl.ru завершен. Получено {len(projects)} проектов")
            
            # Показать первые несколько проектов
            for i, project in enumerate(projects[:3]):
                print(f"  Проект {i+1}: {project.get('title', 'Без названия')}")
                print(f"    Описание: {project.get('description', 'Нет описания')[:100]}...")
                print(f"    Ссылка: {project.get('url', 'Нет ссылки')}")
                print()
        
    except Exception as e:
        print(f"✗ Ошибка при сборе данных с fl.ru: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("Запуск простого теста системы сбора данных...")
    
    # Тестирование только fl.ru
    asyncio.run(test_fl_ru())
    
    print("\nТестирование завершено!")


if __name__ == "__main__":
    main()