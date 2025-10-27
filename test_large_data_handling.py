#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования работы с большими объемами данных.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import time
from datetime import datetime, timedelta

from data_collector import DataCollector
from filter_engine import FilterEngine
from personalization_engine import PersonalizationEngine
from notification_engine import NotificationEngine
from user_settings_manager import UserSettings, UserFilters


class TestLargeDataHandling(unittest.TestCase):
    """Тесты для обработки больших объемов данных"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.mock_data_storage = MagicMock()
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        self.mock_notification_engine = MagicMock(spec=NotificationEngine)
        self.mock_notification_scheduler = MagicMock()
        self.mock_user_interaction_tracker = MagicMock()

    def generate_large_project_dataset(self, count=1000):
        """Генерация большого набора данных проектов для тестирования"""
        projects = []
        for i in range(count):
            project = {
                'title': f'Проект {i}',
                'description': f'Описание проекта {i} с различными технологиями и требованиями',
                'budget': (i % 100) * 1000,  # Бюджет от 0 до 9000
                'region': f'Регион {i % 10}',  # 10 различных регионов
                'technologies': [f'Tech{j}' for j in range(i % 5)],  # 0-4 технологии
                'url': f'https://example.com/project/{i}',
                'date': (datetime.now() - timedelta(days=i % 30)).isoformat(),
                'source': 'test_source',
                'type': 'order' if i % 2 == 0 else 'vacancy',
                'external_id': f'ext_{i}'
            }
            projects.append(project)
        return projects

    def test_filter_large_dataset_performance(self):
        """Тест производительности фильтрации большого набора данных"""
        # Подготовка
        filter_engine = FilterEngine()
        large_dataset = self.generate_large_project_dataset(5000)  # 5000 проектов

        user_filters = UserFilters(
            keywords=['проект'],
            technologies=['Tech1'],
            budget_min=10000,
            budget_max=50000,
            regions=['Регион 1', 'Регион 2'],
            project_types=['order']
        )

        # Замер времени выполнения
        start_time = time.time()
        filtered_projects = filter_engine.filter_projects(large_dataset, user_filters)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Время фильтрации {len(large_dataset)} проектов: {execution_time:.2f} секунд")
        print(f"Количество отфильтрованных проектов: {len(filtered_projects)}")

        # Проверка, что фильтрация завершена без ошибок
        self.assertIsInstance(filtered_projects, list)
        # Проверка, что время выполнения приемлемое (меньше 5 секунд для 5000 проектов)
        self.assertLess(execution_time, 5.0)

    def test_personalization_large_dataset_performance(self):
        """Тест производительности персонализации большого набора данных"""
        # Подготовка
        large_dataset = self.generate_large_project_dataset(3000)  # 3000 проектов

        user_settings = UserSettings(
            user_id=123456,
            subscribed=True,
            filters=UserFilters(
                keywords=['проект'],
                technologies=['Tech1'],
                budget_min=10000,
                budget_max=50000,
                regions=['Регион 1'],
                project_types=['order']
            )
        )

        # Мокаем фильтрацию
        self.mock_filter_engine.filter_projects = MagicMock(return_value=large_dataset[::10])  # Каждый 10-й проект

        personalization_engine = PersonalizationEngine(
            MagicMock(),
            self.mock_filter_engine
        )

        # Замер времени выполнения
        start_time = time.time()
        relevant_projects = personalization_engine.get_relevant_projects_for_user(user_settings, large_dataset)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Время персонализации {len(large_dataset)} проектов для одного пользователя: {execution_time:.2f} секунд")
        print(f"Количество релевантных проектов: {len(relevant_projects)}")

        # Проверка, что персонализация завершена без ошибок
        self.assertIsInstance(relevant_projects, list)
        self.assertLess(execution_time, 2.0)  # Проверяем, что время выполнения приемлемое

    def test_format_large_number_of_project_messages(self):
        """Тест форматирования большого количества сообщений о проектах"""
        # Подготовка
        large_dataset = self.generate_large_project_dataset(1000)  # 1000 проектов
        personalization_engine = PersonalizationEngine(
            MagicMock(),
            MagicMock()
        )

        # Замер времени выполнения
        start_time = time.time()
        formatted_messages = []
        for project in large_dataset:
            message = personalization_engine.format_project_message(project)
            formatted_messages.append(message)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Время форматирования {len(formatted_messages)} сообщений: {execution_time:.2f} секунд")

        # Проверка, что форматирование завершено без ошибок
        self.assertEqual(len(formatted_messages), len(large_dataset))
        self.assertLess(execution_time, 3.0)  # Проверяем, что время выполнения приемлемое

    @patch('data_collector.FlRuCollector')
    @patch('data_collector.WeblancerCollector')
    @patch('data_collector.FreemarketCollector')
    @patch('data_collector.GitHubCollector')
    @patch('data_collector.TelegramCollector')
    def test_data_collection_memory_usage(self, mock_telegram, mock_github, mock_freemarket, mock_weblancer, mock_flru):
        """Тест использования памяти при сборе данных"""
        # Подготовка моков для возврата большого объема данных
        large_project_set = self.generate_large_project_dataset(2000)

        mock_flru_instance = MagicMock()
        mock_flru_instance.__aenter__ = AsyncMock(return_value=mock_flru_instance)
        mock_flru_instance.__aexit__ = AsyncMock(return_value=None)
        mock_flru_instance.fetch_projects = AsyncMock(return_value=large_project_set[:500])
        mock_flru_instance.normalize_project_data = MagicMock(side_effect=lambda x: x)

        mock_weblancer_instance = MagicMock()
        mock_weblancer_instance.__aenter__ = AsyncMock(return_value=mock_weblancer_instance)
        mock_weblancer_instance.__aexit__ = AsyncMock(return_value=None)
        mock_weblancer_instance.fetch_projects = AsyncMock(return_value=large_project_set[500:1000])
        mock_weblancer_instance.normalize_project_data = MagicMock(side_effect=lambda x: x)

        mock_freemarket_instance = MagicMock()
        mock_freemarket_instance.__aenter__ = AsyncMock(return_value=mock_freemarket_instance)
        mock_freemarket_instance.__aexit__ = AsyncMock(return_value=None)
        mock_freemarket_instance.fetch_projects = AsyncMock(return_value=large_project_set[1000:1500])
        mock_freemarket_instance.normalize_project_data = MagicMock(side_effect=lambda x: x)

        mock_github_instance = MagicMock()
        mock_github_instance.__aenter__ = AsyncMock(return_value=mock_github_instance)
        mock_github_instance.__aexit__ = AsyncMock(return_value=None)
        mock_github_instance.fetch_projects = AsyncMock(return_value=large_project_set[1500:2000])
        mock_github_instance.normalize_project_data = MagicMock(side_effect=lambda x: x)

        mock_telegram_instance = MagicMock()
        mock_telegram_instance.__aenter__ = AsyncMock(return_value=mock_telegram_instance)
        mock_telegram_instance.__aexit__ = AsyncMock(return_value=None)
        mock_telegram_instance.initialize = AsyncMock()
        mock_telegram_instance.close = AsyncMock()
        mock_telegram_instance.collect_from_channels = AsyncMock(return_value=[])
        mock_telegram_instance.normalize_project_data = MagicMock(side_effect=lambda x: x)

        # Настройка возвращаемых значений
        mock_flru.return_value = mock_flru_instance
        mock_weblancer.return_value = mock_weblancer_instance
        mock_freemarket.return_value = mock_freemarket_instance
        mock_github.return_value = mock_github_instance
        mock_telegram.return_value = mock_telegram_instance

        # Создаем экземпляр DataCollector с моками
        collector = DataCollector()
        collector.fl_ru_collector = mock_flru_instance
        collector.weblancer_collector = mock_weblancer_instance
        collector.freemarket_collector = mock_freemarket_instance
        collector.github_collector = mock_github_instance
        collector.telegram_collector = mock_telegram_instance

        # Замер времени выполнения
        start_time = time.time()
        async def collect_data():
            return await collector.collect_all_data()
        
        all_projects = asyncio.run(collect_data())
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Время сбора {len(all_projects)} проектов из всех источников: {execution_time:.2f} секунд")

        # Проверка, что сбор данных завершен без ошибок
        self.assertIsInstance(all_projects, list)
        self.assertLess(execution_time, 10.0)  # Проверяем, что время выполнения приемлемое

    def test_notification_engine_bulk_performance(self):
        """Тест производительности массовой отправки уведомлений"""
        # Подготовка большого количества уведомлений
        notifications = {}
        for user_id in range(100):  # 100 пользователей
            user_notifications = []
            for msg_id in range(50):  # 50 сообщений каждому
                user_notifications.append(f"Уведомление {msg_id} для пользователя {user_id}")
            notifications[user_id] = user_notifications

        # Мокаем Bot для уведомлений
        with patch('notification_engine.Bot') as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock(return_value=MagicMock())
            mock_bot_class.return_value = mock_bot

            from user_settings_manager import UserSettingsManager
            notification_engine = NotificationEngine(
                "test_token",
                UserSettingsManager(),
                self.mock_data_storage,
                self.mock_personalization_engine
            )
            notification_engine.bot = mock_bot

            # Замер времени выполнения
            start_time = time.time()
            async def send_notifications():
                return await notification_engine.send_bulk_notifications(notifications)
            
            results = asyncio.run(send_notifications())
            end_time = time.time()

            execution_time = end_time - start_time
            print(f"Время отправки {sum(len(msgs) for msgs in notifications.values())} уведомлений {len(notifications)} пользователям: {execution_time:.2f} секунд")

            # Проверка, что отправка завершена без ошибок
            self.assertIsInstance(results, dict)
            self.assertEqual(len(results), len(notifications))
            self.assertLess(execution_time, 60.0)  # Проверяем, что время выполнения приемлемое (меньше 1 минуты)


class TestMemoryEfficiency(unittest.TestCase):
    """Тесты на эффективность использования памяти"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.mock_data_storage = MagicMock()
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        self.mock_notification_engine = MagicMock(spec=NotificationEngine)

    def generate_large_project_dataset(self, count=100):
        """Генерация большого набора данных проектов для тестирования"""
        projects = []
        for i in range(count):
            project = {
                'title': f'Проект {i}',
                'description': f'Описание проекта {i} с различными технологиями и требованиями',
                'budget': (i % 100) * 1000,
                'region': f'Регион {i % 10}',
                'technologies': [f'Tech{j}' for j in range(i % 5)],
                'url': f'https://example.com/project/{i}',
                'date': (datetime.now() - timedelta(days=i % 30)).isoformat(),
                'source': 'test_source',
                'type': 'order' if i % 2 == 0 else 'vacancy',
                'external_id': f'ext_{i}'
            }
            projects.append(project)
        return projects

    def test_filter_memory_efficiency(self):
        """Тест эффективности использования памяти при фильтрации"""
        import tracemalloc

        filter_engine = FilterEngine()
        large_dataset = self.generate_large_project_dataset(2000)

        user_filters = UserFilters(
            keywords=['проект'],
            technologies=['Tech1'],
            budget_min=10000,
            budget_max=50000,
            regions=['Регион 1'],
            project_types=['order']
        )

        # Запуск отслеживания памяти
        tracemalloc.start()

        # Выполнение фильтрации
        filtered_projects = filter_engine.filter_projects(large_dataset, user_filters)

        # Получение статистики по памяти
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"Текущее использование памяти при фильтрации: {current / 1024 / 1024:.2f} MB")
        print(f"Пик использования памяти при фильтрации: {peak / 1024 / 1024:.2f} MB")

        # Проверка, что память используется разумно (меньше 100 MB для 2000 проектов)
        self.assertLess(peak, 100 * 1024 * 1024)  # 100 MB в байтах

    def test_personalization_memory_efficiency(self):
        """Тест эффективности использования памяти при персонализации"""
        import tracemalloc

        large_dataset = self.generate_large_project_dataset(1500)

        user_settings = UserSettings(
            user_id=123456,
            subscribed=True,
            filters=UserFilters(
                keywords=['проект'],
                technologies=['Tech1'],
                budget_min=10000,
                budget_max=50000,
                regions=['Регион 1'],
                project_types=['order']
            )
        )

        # Мокаем фильтрацию
        self.mock_filter_engine.filter_projects = MagicMock(return_value=large_dataset[::10])  # Каждый 10-й проект

        personalization_engine = PersonalizationEngine(
            MagicMock(),
            self.mock_filter_engine
        )

        # Запуск отслеживания памяти
        tracemalloc.start()

        # Выполнение персонализации
        relevant_projects = personalization_engine.get_relevant_projects_for_user(user_settings, large_dataset)

        # Получение статистики по памяти
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"Текущее использование памяти при персонализации: {current / 1024 / 1024:.2f} MB")
        print(f"Пик использования памяти при персонализации: {peak / 1024 / 1024:.2f} MB")

        # Проверка, что память используется разумно
        self.assertLess(peak, 50 * 1024 * 1024)  # 50 MB в байтах


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()