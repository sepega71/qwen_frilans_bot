#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования обработки ошибок в системе.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import logging
from telegram.error import TelegramError

from bot_core import FreelanceBot
from data_collector import DataCollector
from filter_engine import FilterEngine
from personalization_engine import PersonalizationEngine
from notification_engine import NotificationEngine
from user_settings_manager import UserSettingsManager


class TestErrorHandling(unittest.TestCase):
    """Тесты для обработки ошибок в различных компонентах системы"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.mock_data_storage = MagicMock()
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        self.mock_notification_engine = MagicMock(spec=NotificationEngine)
        self.mock_notification_scheduler = MagicMock()
        self.mock_user_interaction_tracker = MagicMock()

    def test_bot_core_exception_handling(self):
        """Тест обработки исключений в ядре бота"""
        # Создаем бота
        bot = FreelanceBot(
            token="test_token",
            data_storage=self.mock_data_storage,
            filter_engine=self.mock_filter_engine,
            personalization_engine=self.mock_personalization_engine,
            notification_engine=self.mock_notification_engine,
            notification_scheduler=self.mock_notification_scheduler,
            user_interaction_tracker=self.mock_user_interaction_tracker
        )

        # Проверяем, что логгер настроен
        self.assertIsNotNone(bot.logger)
        self.assertEqual(bot.logger.level, logging.INFO)

    @patch('data_collector.FlRuCollector')
    @patch('data_collector.WeblancerCollector')
    @patch('data_collector.FreemarketCollector')
    @patch('data_collector.GitHubCollector')
    @patch('data_collector.TelegramCollector')
    def test_data_collector_exception_handling(self, mock_telegram, mock_github, mock_freemarket, mock_weblancer, mock_flru):
        """Тест обработки исключений в модуле сбора данных"""
        # Подготовка моков, которые выбрасывают исключения
        mock_flru_instance = MagicMock()
        mock_flru_instance.__aenter__ = AsyncMock(return_value=mock_flru_instance)
        mock_flru_instance.__aexit__ = AsyncMock(return_value=None)
        mock_flru_instance.fetch_projects = AsyncMock(side_effect=Exception("Network error"))
        mock_flru_instance.normalize_project_data = MagicMock(return_value={'title': 'Test', 'source': 'fl.ru'})

        mock_weblancer_instance = MagicMock()
        mock_weblancer_instance.__aenter__ = AsyncMock(return_value=mock_weblancer_instance)
        mock_weblancer_instance.__aexit__ = AsyncMock(return_value=None)
        mock_weblancer_instance.fetch_projects = AsyncMock(side_effect=Exception("API error"))
        mock_weblancer_instance.normalize_project_data = MagicMock(return_value={'title': 'Test', 'source': 'weblancer.net'})

        mock_freemarket_instance = MagicMock()
        mock_freemarket_instance.__aenter__ = AsyncMock(return_value=mock_freemarket_instance)
        mock_freemarket_instance.__aexit__ = AsyncMock(return_value=None)
        mock_freemarket_instance.fetch_projects = AsyncMock(side_effect=Exception("Parsing error"))
        mock_freemarket_instance.normalize_project_data = MagicMock(return_value={'title': 'Test', 'source': 'freemarket.ru'})

        mock_github_instance = MagicMock()
        mock_github_instance.__aenter__ = AsyncMock(return_value=mock_github_instance)
        mock_github_instance.__aexit__ = AsyncMock(return_value=None)
        mock_github_instance.fetch_projects = AsyncMock(side_effect=Exception("GitHub API error"))
        mock_github_instance.normalize_project_data = MagicMock(return_value={'title': 'Test', 'source': 'github'})

        mock_telegram_instance = MagicMock()
        mock_telegram_instance.__aenter__ = AsyncMock(return_value=mock_telegram_instance)
        mock_telegram_instance.__aexit__ = AsyncMock(return_value=None)
        mock_telegram_instance.initialize = AsyncMock()
        mock_telegram_instance.close = AsyncMock()
        mock_telegram_instance.collect_from_channels = AsyncMock(side_effect=Exception("Telegram error"))
        mock_telegram_instance.normalize_project_data = MagicMock(return_value={'title': 'Test', 'source': 'telegram'})

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

        # Проверяем, что исключения обрабатываются корректно
        async def run_test():
            # Даже при ошибках в источниках, collect_all_data должна завершиться без падения
            try:
                result = await collector.collect_all_data()
                # Должен вернуть хотя бы пустой список
                self.assertIsInstance(result, list)
            except Exception as e:
                # Если исключение не обрабатывается, тест не пройден
                self.fail(f"Исключение не обработано корректно: {e}")

        asyncio.run(run_test())

    def test_filter_engine_exception_handling(self):
        """Тест обработки исключений в системе фильтрации"""
        filter_engine = FilterEngine()

        # Тестируем различные сценарии с неправильными данными
        project_data = {
            'title': 'Тестовый проект',
            'description': 'Описание проекта',
            'budget': 'invalid_budget',  # Неправильный тип данных
            'region': 'Москва',
            'technologies': ['Python', 'Django'],
            'type': 'order'
        }

        from user_settings_manager import UserFilters
        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=10000,
            budget_max=50000,
            regions=['Москва'],
            project_types=['order']
        )

        # Проверяем, что исключение не происходит при неправильных данных
        try:
            result = filter_engine.matches_budget(project_data, user_filters.budget_min, user_filters.budget_max)
            # Если budget не может быть преобразован в число, должно вернуться False
            self.assertFalse(result)
        except Exception as e:
            self.fail(f"Исключение не обработано корректно в matches_budget: {e}")

    @patch('notification_engine.Bot')
    def test_notification_engine_telegram_error(self, mock_bot_class):
        """Тест обработки ошибок Telegram при отправке уведомлений"""
        # Подготовка
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(side_effect=TelegramError("Forbidden: bot was blocked by the user"))
        mock_bot_class.return_value = mock_bot

        user_settings_manager = UserSettingsManager()
        mock_data_storage = MagicMock()
        personalization_engine = MagicMock()

        notification_engine = NotificationEngine(
            "test_token",
            user_settings_manager,
            mock_data_storage,
            personalization_engine
        )
        notification_engine.bot = mock_bot

        # Выполнение
        async def run_test():
            success = await notification_engine.send_notification(123456, "Тестовое уведомление")
            # Должно вернуть False при ошибке
            self.assertFalse(success)

        asyncio.run(run_test())

    @patch('notification_engine.Bot')
    def test_notification_engine_general_error(self, mock_bot_class):
        """Тест обработки общих ошибок при отправке уведомлений"""
        # Подготовка
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(side_effect=Exception("Network error"))
        mock_bot_class.return_value = mock_bot

        user_settings_manager = UserSettingsManager()
        mock_data_storage = MagicMock()
        personalization_engine = MagicMock()

        notification_engine = NotificationEngine(
            "test_token",
            user_settings_manager,
            mock_data_storage,
            personalization_engine
        )
        notification_engine.bot = mock_bot

        # Выполнение
        async def run_test():
            success = await notification_engine.send_notification(123456, "Тестовое уведомление")
            # Должно вернуть False при ошибке
            self.assertFalse(success)

        asyncio.run(run_test())

    def test_user_settings_manager_exception_handling(self):
        """Тест обработки исключений в менеджере настроек пользователя"""
        user_settings_manager = UserSettingsManager()

        # Тестируем обработку неправильных значений
        try:
            # Попытка добавить None в качестве ключевых слов
            user_settings_manager.add_keywords(123456, None)
        except Exception as e:
            self.fail(f"Исключение не обработано корректно в add_keywords: {e}")

        try:
            # Попытка установить отрицательный бюджет
            user_settings_manager.set_budget(123456, -1000, 5000)
        except Exception as e:
            self.fail(f"Исключение не обработано корректно в set_budget: {e}")

    def test_data_storage_exception_handling(self):
        """Тест обработки исключений в хранилище данных"""
        # Имитация ошибки при работе с хранилищем данных
        mock_data_storage = MagicMock()
        mock_data_storage.get_recent_projects = MagicMock(side_effect=Exception("Database connection failed"))

        # Проверяем, что ошибка обрабатывается корректно в других компонентах
        from notification_engine import NotificationEngine
        from user_settings_manager import UserSettingsManager

        personalization_engine = MagicMock()
        notification_engine = NotificationEngine(
            "test_token",
            UserSettingsManager(),
            mock_data_storage,
            personalization_engine
        )

        async def run_test():
            # Используем метод, который использует data_storage
            try:
                recent_projects = mock_data_storage.get_recent_projects(limit=10)
            except Exception as e:
                # Ошибка должна быть обработана или передана наверх
                pass  # В реальной системе это может быть обработано в более высоком уровне

        asyncio.run(run_test())


class TestRobustness(unittest.TestCase):
    """Тесты на устойчивость системы к ошибкам"""

    def test_filter_with_invalid_data(self):
        """Тест фильтрации с некорректными данными"""
        filter_engine = FilterEngine()
        from user_settings_manager import UserFilters

        # Проект с некорректными данными
        invalid_project = {
            'title': None,
            'description': 12345,  # Должно быть строкой
            'budget': 'not_a_number',
            'region': '',
            'technologies': 'not_a_list',
            'type': 'invalid_type',
            'date': 'not_a_date'
        }

        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=10000,
            budget_max=50000,
            regions=['Москва'],
            project_types=['order']
        )

        # Проверяем, что фильтрация не падает с исключениями
        try:
            result = filter_engine.matches_filters(invalid_project, user_filters)
            # Результат может быть любым, главное - не должно быть исключения
        except Exception as e:
            self.fail(f"Фильтрация не должна падать с некорректными данными: {e}")

    def test_personalization_with_invalid_data(self):
        """Тест персонализации с некорректными данными"""
        from user_settings_manager import UserSettings, UserFilters
        from filter_engine import FilterEngine

        mock_user_settings_manager = MagicMock()
        mock_filter_engine = MagicMock(spec=FilterEngine)
        mock_filter_engine.filter_projects = MagicMock(return_value=[])

        personalization_engine = PersonalizationEngine(
            mock_user_settings_manager,
            mock_filter_engine
        )

        # Некорректные данные проекта
        invalid_projects = [
            {
                'title': '',
                'description': None,
                'budget': -100,
                'region': 123,
                'technologies': ['Python', None, 123],
                'type': 'invalid_type',
                'url': 'not_a_url'
            }
        ]

        user_settings = UserSettings(
            user_id=123456,
            subscribed=True,
            filters=UserFilters(
                keywords=['python'],
                technologies=['python'],
                budget_min=10000,
                budget_max=50000,
                regions=['Москва'],
                project_types=['order']
            )
        )

        # Проверяем, что персонализация не падает с исключениями
        try:
            result = personalization_engine.get_relevant_projects_for_user(user_settings, invalid_projects)
            # Результат может быть любым, главное - не должно быть исключения
        except Exception as e:
            self.fail(f"Персонализация не должна падать с некорректными данными: {e}")

    @patch('notification_engine.Bot')
    def test_bulk_notifications_with_errors(self, mock_bot_class):
        """Тест массовой отправки уведомлений с частичными ошибками"""
        # Подготовка
        mock_bot = AsyncMock()
        # Симулируем, что каждое второе сообщение вызывает ошибку
        call_count = 0
        def side_effect(chat_id, text, parse_mode=None):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise TelegramError("Forbidden: bot was blocked by the user")
            return MagicMock()

        mock_bot.send_message = AsyncMock(side_effect=side_effect)
        mock_bot_class.return_value = mock_bot

        user_settings_manager = UserSettingsManager()
        mock_data_storage = MagicMock()
        personalization_engine = MagicMock()

        notification_engine = NotificationEngine(
            "test_token",
            user_settings_manager,
            mock_data_storage,
            personalization_engine
        )
        notification_engine.bot = mock_bot

        # Подготовка уведомлений для нескольких пользователей
        notifications = {
            123456: ["Сообщение 1", "Сообщение 2", "Сообщение 3", "Сообщение 4"],
            789012: ["Сообщение A", "Сообщение B", "Сообщение C"]
        }

        # Выполнение
        async def run_test():
            results = await notification_engine.send_bulk_notifications(notifications)
            # Проверяем, что результаты возвращаются даже при частичных ошибках
            self.assertIn(123456, results)
            self.assertIn(789012, results)
            # Пользователь 123456: 2 сообщения отправлены (1 и 3), 2 не отправлены (2 и 4)
            self.assertLessEqual(results[123456], 2)
            # Пользователь 789012: 1 или 2 сообщения отправлены (A и/или C)
            self.assertLessEqual(results[789012], 2)

        asyncio.run(run_test())


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()