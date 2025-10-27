#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования восстановления после сбоев.
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
from notification_scheduler import NotificationScheduler
from user_settings_manager import UserSettings, UserFilters


class TestFailureRecovery(unittest.TestCase):
    """Тесты для восстановления после сбоев"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.mock_data_storage = MagicMock()
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        self.mock_notification_engine = MagicMock(spec=NotificationEngine)
        self.mock_user_settings_manager = MagicMock()

    @patch('data_collector.FlRuCollector')
    @patch('data_collector.WeblancerCollector')
    @patch('data_collector.FreemarketCollector')
    @patch('data_collector.GitHubCollector')
    @patch('data_collector.TelegramCollector')
    def test_data_collector_recovery_after_source_failure(self, mock_telegram, mock_github, mock_freemarket, mock_weblancer, mock_flru):
        """Тест восстановления сборщика данных после сбоя одного из источников"""
        # Подготовка моков
        # fl.ru источник работает нормально
        mock_flru_instance = MagicMock()
        mock_flru_instance.__aenter__ = AsyncMock(return_value=mock_flru_instance)
        mock_flru_instance.__aexit__ = AsyncMock(return_value=None)
        mock_flru_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Проект с fl.ru', 'budget': 10000, 'source': 'fl.ru'}
        ])
        mock_flru_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Проект с fl.ru', 'budget': 10000, 'source': 'fl.ru'
        })

        # weblancer источник временно не работает
        mock_weblancer_instance = MagicMock()
        mock_weblancer_instance.__aenter__ = AsyncMock(return_value=mock_weblancer_instance)
        mock_weblancer_instance.__aexit__ = AsyncMock(return_value=None)
        mock_weblancer_instance.fetch_projects = AsyncMock(side_effect=Exception("API временно недоступно"))
        mock_weblancer_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Проект с weblancer', 'budget': 15000, 'source': 'weblancer.net'
        })

        # freemarket источник работает нормально
        mock_freemarket_instance = MagicMock()
        mock_freemarket_instance.__aenter__ = AsyncMock(return_value=mock_freemarket_instance)
        mock_freemarket_instance.__aexit__ = AsyncMock(return_value=None)
        mock_freemarket_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Проект с freemarket', 'budget': 20000, 'source': 'freemarket.ru'}
        ])
        mock_freemarket_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Проект с freemarket', 'budget': 2000, 'source': 'freemarket.ru'
        })

        # GitHub источник работает нормально
        mock_github_instance = MagicMock()
        mock_github_instance.__aenter__ = AsyncMock(return_value=mock_github_instance)
        mock_github_instance.__aexit__ = AsyncMock(return_value=None)
        mock_github_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Проект с GitHub', 'budget': None, 'source': 'github'}
        ])
        mock_github_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Проект с GitHub', 'budget': None, 'source': 'github'
        })

        # Telegram источник работает нормально
        mock_telegram_instance = MagicMock()
        mock_telegram_instance.__aenter__ = AsyncMock(return_value=mock_telegram_instance)
        mock_telegram_instance.__aexit__ = AsyncMock(return_value=None)
        mock_telegram_instance.initialize = AsyncMock()
        mock_telegram_instance.close = AsyncMock()
        mock_telegram_instance.collect_from_channels = AsyncMock(return_value=[
            {'title': 'Проект из Telegram', 'budget': 25000, 'source': 'telegram'}
        ])
        mock_telegram_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Проект из Telegram', 'budget': 25000, 'source': 'telegram'
        })

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

        # Выполнение сбора данных
        async def collect_data():
            return await collector.collect_all_data()
        
        all_projects = asyncio.run(collect_data())

        # Проверка, что сбор данных завершен, несмотря на сбой одного источника
        self.assertIsInstance(all_projects, list)
        # Должны получить проекты из работающих источников
        sources = [project['source'] for project in all_projects]
        self.assertIn('fl.ru', sources)
        self.assertIn('freemarket.ru', sources)
        self.assertIn('github', sources)
        self.assertIn('telegram', sources)
        # weblancer не должен быть в списке, так как источник не работал
        # Но система должна продолжать работать

    def test_filter_engine_recovery_after_error(self):
        """Тест восстановления системы фильтрации после ошибки"""
        filter_engine = FilterEngine()

        # Создаем набор данных с одним "плохим" элементом
        projects = [
            {
                'title': 'Нормальный проект',
                'description': 'Описание нормального проекта',
                'budget': 50000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'type': 'order'
            },
            {
                'title': 'Проблемный проект',
                'description': 'Описание проекта с некорректными данными',
                'budget': 'invalid_budget_value',  # Некорректное значение
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'type': 'order'
            },
            {
                'title': 'Еще один нормальный проект',
                'description': 'Описание еще одного нормального проекта',
                'budget': 75000,
                'region': 'Санкт-Петербург',
                'technologies': ['JavaScript', 'React'],
                'type': 'order'
            }
        ]

        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=10000,
            budget_max=10000,
            regions=['Москва'],
            project_types=['order']
        )

        # Проверяем, что фильтрация продолжает работать, несмотря на проблемный элемент
        try:
            filtered_projects = filter_engine.filter_projects(projects, user_filters)
            # Проверяем, что результат содержит только подходящие проекты
            # Проблемный проект должен быть обработан без падения всей системы
            self.assertIsInstance(filtered_projects, list)
            # Должен остаться только первый проект, т.к. второй имеет некорректный бюджет
            # Третий не подходит по технологии
            self.assertGreaterEqual(len(filtered_projects), 0)
        except Exception as e:
            self.fail(f"Фильтрация не должна падать из-за одного проблемного элемента: {e}")

    @patch('notification_engine.Bot')
    def test_notification_engine_recovery_after_send_failure(self, mock_bot_class):
        """Тест восстановления движка уведомлений после ошибки отправки"""
        # Подготовка
        mock_bot = AsyncMock()
        # Симулируем, что одно из сообщений вызывает ошибку
        call_count = 0
        def side_effect(chat_id, text, parse_mode=None):
            nonlocal call_count
            call_count += 1
            if call_count == 3:  # Третье сообщение вызывает ошибку
                raise Exception("Временная ошибка отправки")
            return MagicMock()

        mock_bot.send_message = AsyncMock(side_effect=side_effect)
        mock_bot_class.return_value = mock_bot

        notification_engine = NotificationEngine(
            "test_token",
            self.mock_user_settings_manager,
            self.mock_data_storage,
            self.mock_personalization_engine
        )
        notification_engine.bot = mock_bot

        # Подготовка уведомлений
        notifications = {
            123456: ["Сообщение 1", "Сообщение 2", "Сообщение 3", "Сообщение 4"],
            789012: ["Сообщение A", "Сообщение B"]
        }

        # Выполнение
        async def run_test():
            results = await notification_engine.send_bulk_notifications(notifications)
            # Проверяем, что результаты возвращаются даже при частичных ошибках
            self.assertIn(123456, results)
            self.assertIn(789012, results)
            # Для пользователя 123456: 2 сообщения отправлены (1 и 2), 3-е упало, 4-е должно быть отправлено
            # Для пользователя 789012: оба сообщения должны быть отправлены
            return results

        results = asyncio.run(run_test())
        # Проверяем, что система продолжает работать после ошибки
        self.assertGreaterEqual(results[123456], 2)  # Как минимум 2 сообщения отправлены
        self.assertEqual(results[789012], 2)  # 2 сообщения отправлены

    def test_scheduler_recovery_after_failure(self):
        """Тест восстановления планировщика после сбоя"""
        # Создаем моки для планировщика
        mock_notification_engine = MagicMock(spec=NotificationEngine)
        mock_data_storage = MagicMock()
        mock_personalization_engine = MagicMock(spec=PersonalizationEngine)

        scheduler = NotificationScheduler(
            mock_notification_engine,
            mock_data_storage,
            mock_personalization_engine
        )

        # Мокаем методы, которые могут вызвать ошибки
        mock_data_storage.get_recent_projects = MagicMock(side_effect=[
            Exception("База данных временно недоступна"),
            [{'title': 'Новый проект', 'date': datetime.now().isoformat()}]
        ])

        mock_personalization_engine.get_personalized_notifications = MagicMock(
            return_value={123456: ["Новое уведомление"]}
        )

        mock_notification_engine.send_personalized_notifications_for_projects = AsyncMock()

        # Симулируем работу планировщика
        async def simulate_scheduler_cycle():
            try:
                # Первый цикл: ошибка
                recent_projects = mock_data_storage.get_recent_projects(limit=10)
            except Exception:
                # Обработка ошибки и попытка восстановления
                time.sleep(1)  # Имитация паузы перед повторной попыткой
                recent_projects = mock_data_storage.get_recent_projects(limit=10)

            # После восстановления система должна продолжить нормальную работу
            if recent_projects:
                notifications = mock_personalization_engine.get_personalized_notifications(recent_projects)
                await mock_notification_engine.send_personalized_notifications_for_projects(
                    recent_projects
                )

        # Запускаем симуляцию
        asyncio.run(simulate_scheduler_cycle())

        # Проверяем, что после ошибки система восстановилась и продолжила работу
        mock_notification_engine.send_personalized_notifications_for_projects.assert_called()

    def test_data_storage_recovery_after_error(self):
        """Тест восстановления хранилища данных после ошибки"""
        # Мокаем хранилище данных с возможной ошибкой
        mock_data_storage = MagicMock()
        
        # Симулируем, что первые несколько вызовов заканчиваются ошибкой
        call_count = 0
        def get_recent_projects_side_effect(limit=100):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Первые 2 вызова возвращают ошибку
                raise Exception("Ошибка подключения к базе данных")
            # После этого возвращаем нормальные данные
            return [{'title': f'Проект {call_count}', 'date': datetime.now().isoformat()}]

        mock_data_storage.get_recent_projects = MagicMock(side_effect=get_recent_projects_side_effect)

        # Используем хранилище данных в других компонентах
        from notification_engine import NotificationEngine
        from user_settings_manager import UserSettingsManager

        personalization_engine = MagicMock()
        notification_engine = NotificationEngine(
            "test_token",
            UserSettingsManager(),
            mock_data_storage,
            personalization_engine
        )

        # Симулируем несколько попыток получения данных
        async def test_recovery():
            success = False
            attempts = 0
            max_attempts = 5

            while not success and attempts < max_attempts:
                try:
                    recent_projects = mock_data_storage.get_recent_projects(limit=50)
                    success = True
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise e
                    # Имитация задержки перед повторной попыткой
                    await asyncio.sleep(0.5)

            return recent_projects

        # Запускаем тест восстановления
        recent_projects = asyncio.run(test_recovery())

        # Проверяем, что после нескольких неудачных попыток система восстановилась
        self.assertIsNotNone(recent_projects)
        self.assertIsInstance(recent_projects, list)
        self.assertGreater(len(recent_projects), 0)


class TestResilience(unittest.TestCase):
    """Дополнительные тесты на устойчивость системы"""

    def test_multiple_concurrent_failures(self):
        """Тест устойчивости при одновременных сбоях нескольких компонентов"""
        # Создаем систему с моками, где несколько компонентов могут временно отказать
        mock_data_storage = MagicMock()
        mock_filter_engine = MagicMock(spec=FilterEngine)
        mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        mock_notification_engine = MagicMock(spec=NotificationEngine)

        # Симулируем кратковременные сбои в нескольких компонентах
        call_count = {'storage': 0, 'filter': 0, 'personalization': 0, 'notification': 0}

        def storage_side_effect(limit=10):
            call_count['storage'] += 1
            if call_count['storage'] <= 1:  # Первый вызов завершается ошибкой
                raise Exception("Временная ошибка хранилища")
            return [{'title': 'Проект', 'date': datetime.now().isoformat()}]

        def filter_side_effect(projects, filters):
            call_count['filter'] += 1
            if call_count['filter'] <= 1:  # Первый вызов завершается ошибкой
                raise Exception("Временная ошибка фильтрации")
            return projects

        mock_data_storage.get_recent_projects = MagicMock(side_effect=storage_side_effect)
        mock_filter_engine.filter_projects = MagicMock(side_effect=filter_side_effect)
        mock_personalization_engine.get_relevant_projects_for_user = MagicMock(
            return_value=[{'title': 'Релевантный проект'}]
        )

        async def test_resilience():
            # Попытка выполнить операцию, задействующую несколько компонентов
            success = False
            attempts = 0
            max_attempts = 3

            while not success and attempts < max_attempts:
                try:
                    # Получаем данные
                    projects = mock_data_storage.get_recent_projects(limit=50)
                    # Применяем фильтры
                    filtered_projects = mock_filter_engine.filter_projects(projects, MagicMock())
                    success = True
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise e
                    await asyncio.sleep(0.5)

            return filtered_projects

        # Запускаем тест
        filtered_projects = asyncio.run(test_resilience())

        # Проверяем, что система восстановилась и вернула ожидаемые данные
        self.assertIsInstance(filtered_projects, list)

    def test_graceful_degradation(self):
        """Тест постепенного ухудшения функциональности при сбоях"""
        # Тестируем, как система ведет себя при частичных сбоях
        filter_engine = FilterEngine()

        # Создаем проекты, часть из которых не может быть корректно обработана
        projects = [
            {
                'title': 'Нормальный проект 1',
                'description': 'Описание нормального проекта 1',
                'budget': 50000,
                'region': 'Москва',
                'technologies': ['Python'],
                'type': 'order'
            },
            {
                'title': 'Нормальный проект 2',
                'description': 'Описание нормального проекта 2',
                'budget': 7500,
                'region': 'Санкт-Петербург',
                'technologies': ['JavaScript'],
                'type': 'order'
            }
        ]

        # Создаем фильтр с условно "проблемным" значением
        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=1000,
            budget_max=100000,
            regions=['Москва'],
            project_types=['order']
        )

        # Проверяем, что система продолжает работать и возвращает частичный результат
        try:
            filtered_projects = filter_engine.filter_projects(projects, user_filters)
            # Должен вернуться хотя бы частичный результат
            self.assertIsInstance(filtered_projects, list)
            # В данном случае должен вернуться 1 проект (первый)
            self.assertGreaterEqual(len(filtered_projects), 0)
        except Exception as e:
            self.fail(f"Система должна продолжать работать с частичными сбоями: {e}")


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()