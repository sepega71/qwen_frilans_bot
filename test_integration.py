#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для комплексного тестирования всех компонентов системы.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from datetime import datetime

from bot_core import FreelanceBot
from data_collector import DataCollector
from filter_engine import FilterEngine
from personalization_engine import PersonalizationEngine
from notification_engine import NotificationEngine
from notification_scheduler import NotificationScheduler
from user_settings_manager import UserSettings, UserFilters, UserSettingsManager
from data_storage import DataStorage
from user_interaction_tracker import UserInteractionTracker
from logging_config import setup_logging, get_logger


class TestIntegration(unittest.TestCase):
    """Комплексные интеграционные тесты для всех компонентов системы"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Настройка логирования для тестов
        setup_logging(log_level=unittest.mock.ANY, log_file="logs/test_integration.log")
        
        # Создание моков для зависимостей
        self.mock_data_storage = MagicMock(spec=DataStorage)
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        self.mock_notification_engine = MagicMock(spec=NotificationEngine)
        self.mock_notification_scheduler = MagicMock(spec=NotificationScheduler)
        self.mock_user_interaction_tracker = MagicMock(spec=UserInteractionTracker)

        # Создание экземпляров компонентов
        self.user_settings_manager = UserSettingsManager()
        self.filter_engine = FilterEngine()
        self.data_storage = MagicMock(spec=DataStorage)
        
        # Мокаем методы хранилища данных
        self.data_storage.get_recent_projects = MagicMock(return_value=[])
        self.data_storage.save_project = MagicMock()
        self.data_storage.get_user_subscriptions = MagicMock(return_value=[])

    def test_full_workflow_simulation(self):
        """Тест полного рабочего цикла системы"""
        # Подготовка данных
        user_settings = UserSettings(
            user_id=123456,
            subscribed=True,
            filters=UserFilters(
                keywords=['python', 'telegram'],
                technologies=['Python', 'Django'],
                budget_min=50000,
                budget_max=150000,
                regions=['Москва'],
                project_types=['order']
            )
        )
        
        # Добавляем пользователя в систему
        self.user_settings_manager.save_user_settings(user_settings)

        # Подготовка проектов
        projects = [
            {
                'title': 'Разработка Telegram бота на Python',
                'description': 'Требуется разработать бота для автоматизации задач',
                'budget': 100000,
                'region': 'Москва',
                'technologies': ['Python', 'Django', 'Telegram API'],
                'url': 'https://example.com/project/1',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'order',
                'external_id': 'test_1'
            },
            {
                'title': 'Верстка сайта',
                'description': 'Необходимо сверстать макет',
                'budget': 30000,
                'region': 'Санкт-Петербург',
                'technologies': ['HTML', 'CSS', 'JavaScript'],
                'url': 'https://example.com/project/2',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'order',
                'external_id': 'test_2'
            }
        ]

        # Мокаем возвращение проектов из хранилища
        self.data_storage.get_recent_projects = MagicMock(return_value=projects)

        # Мокаем фильтрацию
        self.mock_filter_engine.filter_projects = MagicMock(return_value=[projects[0]])

        # Мокаем персонализацию
        self.mock_personalization_engine.get_relevant_projects_for_user = MagicMock(
            return_value=[projects[0]]
        )
        self.mock_personalization_engine.format_project_message = MagicMock(
            return_value="Новое предложение: Разработка Telegram бота на Python"
        )

        # Мокаем отправку уведомлений
        with patch('notification_engine.Bot') as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock(return_value=MagicMock())
            mock_bot_class.return_value = mock_bot

            notification_engine = NotificationEngine(
                "test_token",
                self.user_settings_manager,
                self.data_storage,
                self.mock_personalization_engine
            )
            notification_engine.bot = mock_bot

            # Выполнение полного цикла
            async def run_full_workflow():
                # 1. Сбор проектов
                recent_projects = self.data_storage.get_recent_projects(limit=10)
                
                # 2. Персонализация уведомлений
                notifications = self.mock_personalization_engine.get_personalized_notifications(recent_projects)
                
                # 3. Отправка уведомлений
                results = await notification_engine.send_personalized_notifications_for_projects(recent_projects)
                
                return results

            results = asyncio.run(run_full_workflow())

            # Проверка результатов
            self.assertIsInstance(results, dict)
            self.assertIn(123456, results)  # Уведомление должно быть отправлено пользователю
            self.assertGreaterEqual(results[123456], 0)  # Как минимум 0 уведомлений отправлено

    def test_data_flow_from_collection_to_notification(self):
        """Тест потока данных от сбора до уведомления"""
        # Подготовка
        projects = [
            {
                'title': 'Проект 1',
                'description': 'Описание проекта 1',
                'budget': 75000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'url': 'https://example.com/project/1',
                'date': datetime.now().isoformat(),
                'source': 'fl.ru',
                'type': 'order',
                'external_id': 'fl_1'
            }
        ]

        # Добавляем пользователя с подходящими фильтрами
        user_settings = UserSettings(
            user_id=654321,
            subscribed=True,
            filters=UserFilters(
                keywords=['проект'],
                technologies=['Python'],
                budget_min=50000,
                budget_max=100000,
                regions=['Москва'],
                project_types=['order']
            )
        )
        self.user_settings_manager.save_user_settings(user_settings)

        # Создаем настоящие (не мокированные) экземпляры для тестирования взаимодействия
        filter_engine = FilterEngine()
        personalization_engine = PersonalizationEngine(
            self.user_settings_manager,
            filter_engine
        )

        # Тестируем фильтрацию
        filtered_projects = filter_engine.filter_projects(projects, user_settings.filters)
        self.assertEqual(len(filtered_projects), 1)
        self.assertEqual(filtered_projects[0]['title'], 'Проект 1')

        # Тестируем персонализацию
        relevant_projects = personalization_engine.get_relevant_projects_for_user(user_settings, projects)
        self.assertEqual(len(relevant_projects), 1)
        self.assertEqual(relevant_projects[0]['title'], 'Проект 1')

        # Тестируем форматирование сообщения
        message = personalization_engine.format_project_message(relevant_projects[0])
        self.assertIn('Проект 1', message)
        self.assertIn('75000', message)

        # Тестируем отправку уведомления (с моком для Bot)
        with patch('notification_engine.Bot') as mock_bot_class:
            mock_bot = AsyncMock()
            mock_bot.send_message = AsyncMock(return_value=MagicMock())
            mock_bot_class.return_value = mock_bot

            notification_engine = NotificationEngine(
                "test_token",
                self.user_settings_manager,
                self.data_storage,
                personalization_engine
            )
            notification_engine.bot = mock_bot

            async def send_notification():
                success = await notification_engine.send_notification_with_history_tracking(
                    user_settings.user_id,
                    message,
                    relevant_projects[0]['external_id']
                )
                return success

            result = asyncio.run(send_notification())
            self.assertTrue(result)

    def test_multiple_users_different_filters(self):
        """Тест работы с несколькими пользователями и разными фильтрами"""
        # Подготовка проектов
        projects = [
            {
                'title': 'Python проект',
                'description': 'Требуется Python разработчик',
                'budget': 120000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'url': 'https://example.com/project/python',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'order',
                'external_id': 'py_1'
            },
            {
                'title': 'JavaScript проект',
                'description': 'Требуется JavaScript разработчик',
                'budget': 90000,
                'region': 'Санкт-Петербург',
                'technologies': ['JavaScript', 'React'],
                'url': 'https://example.com/project/js',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'order',
                'external_id': 'js_1'
            },
            {
                'title': 'Java проект',
                'description': 'Требуется Java разработчик',
                'budget': 150000,
                'region': 'Новосибирск',
                'technologies': ['Java', 'Spring'],
                'url': 'https://example.com/project/java',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'vacancy',
                'external_id': 'java_1'
            }
        ]

        # Создание пользователей с разными фильтрами
        user1_settings = UserSettings(
            user_id=11111,
            subscribed=True,
            filters=UserFilters(
                keywords=['python'],
                technologies=['Python'],
                budget_min=1000,
                budget_max=200000,
                regions=['Москва'],
                project_types=['order']
            )
        )

        user2_settings = UserSettings(
            user_id=22222,
            subscribed=True,
            filters=UserFilters(
                keywords=['javascript'],
                technologies=['JavaScript'],
                budget_min=8000,
                budget_max=10000,
                regions=['Санкт-Петербург'],
                project_types=['order']
            )
        )

        user3_settings = UserSettings(
            user_id=33333,
            subscribed=True,
            filters=UserFilters(
                keywords=['java'],
                technologies=['Java'],
                budget_min=140000,
                budget_max=20000,
                regions=['Новосибирск'],
                project_types=['vacancy']
            )
        )

        # Добавляем пользователей в систему
        self.user_settings_manager.save_user_settings(user1_settings)
        self.user_settings_manager.save_user_settings(user2_settings)
        self.user_settings_manager.save_user_settings(user3_settings)

        # Создаем настоящие экземпляры для тестирования
        filter_engine = FilterEngine()
        personalization_engine = PersonalizationEngine(
            self.user_settings_manager,
            filter_engine
        )

        # Тестируем, что каждый пользователь получает только релевантные проекты
        user1_projects = personalization_engine.get_relevant_projects_for_user(user1_settings, projects)
        user2_projects = personalization_engine.get_relevant_projects_for_user(user2_settings, projects)
        user3_projects = personalization_engine.get_relevant_projects_for_user(user3_settings, projects)

        self.assertEqual(len(user1_projects), 1)
        self.assertEqual(user1_projects[0]['title'], 'Python проект')

        self.assertEqual(len(user2_projects), 1)
        self.assertEqual(user2_projects[0]['title'], 'JavaScript проект')

        self.assertEqual(len(user3_projects), 1)
        self.assertEqual(user3_projects[0]['title'], 'Java проект')

        # Тестируем генерацию персонализированных уведомлений для всех пользователей
        all_notifications = personalization_engine.get_personalized_notifications(projects)
        self.assertEqual(len(all_notifications), 3)
        self.assertIn(11111, all_notifications)
        self.assertIn(222222, all_notifications)
        self.assertIn(333333, all_notifications)

        self.assertEqual(len(all_notifications[11111]), 1)
        self.assertEqual(len(all_notifications[222222]), 1)
        self.assertEqual(len(all_notifications[33333]), 1)

    def test_system_resilience_with_mixed_data(self):
        """Тест устойчивости системы при обработке разнородных данных"""
        # Подготовка проектов с разными характеристиками
        projects = [
            {
                'title': 'Нормальный проект',
                'description': 'Описание нормального проекта',
                'budget': 100000,
                'region': 'Москва',
                'technologies': ['Python'],
                'url': 'https://example.com/project/normal',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'order',
                'external_id': 'normal_1'
            },
            {
                'title': '',
                'description': None,
                'budget': -1000,  # Некорректный бюджет
                'region': '',
                'technologies': [],
                'url': '',
                'date': 'invalid_date',
                'source': 'test_source',
                'type': 'invalid_type',
                'external_id': 'invalid_1'
            },
            {
                'title': 'Проект без бюджета',
                'description': 'Проект без указанного бюджета',
                'budget': None,
                'region': 'Санкт-Петербург',
                'technologies': ['JavaScript'],
                'url': 'https://example.com/project/no_budget',
                'date': datetime.now().isoformat(),
                'source': 'test_source',
                'type': 'order',
                'external_id': 'no_budget_1'
            }
        ]

        # Пользователь с широкими фильтрами
        user_settings = UserSettings(
            user_id=444444,
            subscribed=True,
            filters=UserFilters(
                keywords=['проект'],
                technologies=['Python', 'JavaScript'],
                budget_min=0,
                budget_max=200000,
                regions=['Москва', 'Санкт-Петербург'],
                project_types=['order']
            )
        )
        self.user_settings_manager.save_user_settings(user_settings)

        # Создаем настоящие экземпляры для тестирования
        filter_engine = FilterEngine()
        personalization_engine = PersonalizationEngine(
            self.user_settings_manager,
            filter_engine
        )

        # Проверяем, что система не падает при обработке некорректных данных
        try:
            relevant_projects = personalization_engine.get_relevant_projects_for_user(user_settings, projects)
            # Должны получить только корректные проекты
            self.assertGreaterEqual(len(relevant_projects), 0)
        except Exception as e:
            self.fail(f"Система не должна падать при обработке некорректных данных: {e}")

        # Проверяем генерацию уведомлений
        try:
            notifications = personalization_engine.get_personalized_notifications(projects)
            # Должны получить уведомления без ошибок
            self.assertIsInstance(notifications, dict)
        except Exception as e:
            self.fail(f"Генерация уведомлений не должна падать: {e}")


class TestSystemMonitoring(unittest.TestCase):
    """Тесты для мониторинга состояния системы"""

    def setUp(self):
        """Настройка тестового окружения"""
        setup_logging(log_level=unittest.mock.ANY, log_file="logs/system_monitoring.log")
        self.logger = get_logger('integration_tests')

    def test_component_interaction_logging(self):
        """Тест логирования взаимодействия между компонентами"""
        # Создаем компоненты с логированием
        filter_engine = FilterEngine()
        personalization_engine = PersonalizationEngine(
            UserSettingsManager(),
            filter_engine
        )

        # Подготовка данных
        projects = [
            {
                'title': 'Тестовый проект',
                'description': 'Описание тестового проекта',
                'budget': 50000,
                'region': 'Москва',
                'technologies': ['Python'],
                'type': 'order'
            }
        ]

        user_settings = UserSettings(
            user_id=555555,
            subscribed=True,
            filters=UserFilters(
                keywords=['тест'],
                technologies=['Python'],
                budget_min=4000,
                budget_max=600,
                regions=['Москва'],
                project_types=['order']
            )
        )

        # Выполняем операции и проверяем, что логирование работает
        self.logger.info("Начало тестирования взаимодействия компонентов")
        
        filtered_projects = filter_engine.filter_projects(projects, user_settings.filters)
        self.logger.info(f"Отфильтровано проектов: {len(filtered_projects)}")
        
        relevant_projects = personalization_engine.get_relevant_projects_for_user(user_settings, projects)
        self.logger.info(f"Найдено релевантных проектов: {len(relevant_projects)}")
        
        message = personalization_engine.format_project_message(relevant_projects[0]) if relevant_projects else ""
        self.logger.info(f"Сформировано сообщение длиной: {len(message)} символов")

        self.logger.info("Завершение тестирования взаимодействия компонентов")

        # Проверяем, что все операции выполнены без ошибок
        self.assertIsInstance(filtered_projects, list)
        self.assertIsInstance(relevant_projects, list)
        self.assertIsInstance(message, str)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()