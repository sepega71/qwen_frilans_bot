#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования системы персонализации.
"""

import unittest
from unittest.mock import MagicMock
from personalization_engine import PersonalizationEngine
from user_settings_manager import UserSettings, UserFilters
from filter_engine import FilterEngine


class TestPersonalizationEngine(unittest.TestCase):
    """Тесты для системы персонализации"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.mock_user_settings_manager = MagicMock()
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.personalization_engine = PersonalizationEngine(
            self.mock_user_settings_manager,
            self.mock_filter_engine
        )

    def test_get_relevant_projects_for_user_subscribed(self):
        """Тест получения релевантных проектов для подписанного пользователя"""
        # Подготовка
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

        projects = [
            {
                'title': 'Разработка Telegram бота на Python',
                'description': 'Требуется разработать бота для автоматизации задач',
                'budget': 30000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'type': 'order'
            },
            {
                'title': 'Верстка сайта',
                'description': 'Необходимо сверстать макет',
                'budget': 15000,
                'region': 'Санкт-Петербург',
                'technologies': ['HTML', 'CSS'],
                'type': 'order'
            }
        ]

        # Мокаем фильтрацию
        self.mock_filter_engine.filter_projects = MagicMock(return_value=[projects[0]])

        # Выполнение
        result = self.personalization_engine.get_relevant_projects_for_user(user_settings, projects)

        # Проверка
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Разработка Telegram бота на Python')
        self.mock_filter_engine.filter_projects.assert_called_once_with(projects, user_settings.filters)

    def test_get_relevant_projects_for_user_unsubscribed(self):
        """Тест получения релевантных проектов для неподписанного пользователя"""
        # Подготовка
        user_settings = UserSettings(
            user_id=123456,
            subscribed=False,
            filters=UserFilters(
                keywords=['python'],
                technologies=['python'],
                budget_min=10000,
                budget_max=50000,
                regions=['Москва'],
                project_types=['order']
            )
        )

        projects = [
            {
                'title': 'Разработка Telegram бота на Python',
                'description': 'Требуется разработать бота для автоматизации задач',
                'budget': 3000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'type': 'order'
            }
        ]

        # Выполнение
        result = self.personalization_engine.get_relevant_projects_for_user(user_settings, projects)

        # Проверка
        self.assertEqual(len(result), 0)

    def test_get_relevant_projects_for_all_users(self):
        """Тест получения релевантных проектов для всех пользователей"""
        # Подготовка
        user_settings_1 = UserSettings(
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

        user_settings_2 = UserSettings(
            user_id=789012,
            subscribed=True,
            filters=UserFilters(
                keywords=['javascript'],
                technologies=['javascript'],
                budget_min=5000,
                budget_max=20000,
                regions=['Санкт-Петербург'],
                project_types=['order']
            )
        )

        projects = [
            {
                'title': 'Разработка Telegram бота на Python',
                'description': 'Требуется разработать бота для автоматизации задач',
                'budget': 30000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'type': 'order'
            },
            {
                'title': 'Верстка сайта на JavaScript',
                'description': 'Необходимо сверстать макет',
                'budget': 15000,
                'region': 'Санкт-Петербург',
                'technologies': ['HTML', 'CSS', 'JavaScript'],
                'type': 'order'
            }
        ]

        # Мокаем получение подписанных пользователей
        self.mock_user_settings_manager.get_subscribed_users = MagicMock(
            return_value=[user_settings_1, user_settings_2]
        )

        # Мокаем фильтрацию для каждого пользователя
        self.mock_filter_engine.filter_projects = MagicMock(
            side_effect=[
                [projects[0]],  # Для первого пользователя
                [projects[1]]   # Для второго пользователя
            ]
        )

        # Выполнение
        result = self.personalization_engine.get_relevant_projects_for_all_users(projects)

        # Проверка
        self.assertEqual(len(result), 2)
        self.assertIn(123456, result)
        self.assertIn(789012, result)
        self.assertEqual(len(result[123456]), 1)
        self.assertEqual(len(result[789012]), 1)
        self.assertEqual(result[123456][0]['title'], 'Разработка Telegram бота на Python')
        self.assertEqual(result[789012][0]['title'], 'Верстка сайта на JavaScript')

    def test_format_project_message_basic(self):
        """Тест форматирования сообщения о проекте (базовый)"""
        # Подготовка
        project = {
            'title': 'Разработка Telegram бота',
            'description': 'Необходимо разработать бота для автоматизации задач',
            'budget': 50000,
            'region': 'Москва',
            'type': 'order',
            'technologies': ['Python', 'Telegram API'],
            'url': 'https://example.com/project/1'
        }

        # Выполнение
        result = self.personalization_engine.format_project_message(project)

        # Проверка
        self.assertIn('🆕 Заказ', result)
        self.assertIn('📝 <b>Разработка Telegram бота</b>', result)
        self.assertIn('📋 <i>Необходимо разработать бота для автоматизации задач</i>', result)
        self.assertIn('💰 Бюджет: 50000 руб.', result)
        self.assertIn('🌍 Регион: Москва', result)
        self.assertIn('🛠️ Технологии: Python, Telegram API', result)
        self.assertIn('🔗 Ссылка: https://example.com/project/1', result)

    def test_format_project_message_long_description(self):
        """Тест форматирования сообщения о проекте (длинное описание)"""
        # Подготовка
        long_description = 'A' * 400  # 400 символов
        project = {
            'title': 'Разработка Telegram бота',
            'description': long_description,
            'budget': 50000,
            'region': 'Москва',
            'type': 'order',
            'technologies': ['Python', 'Telegram API'],
            'url': 'https://example.com/project/1'
        }

        # Выполнение
        result = self.personalization_engine.format_project_message(project)

        # Проверка
        self.assertIn('...', result)
        # Проверяем, что длина описания ограничена
        desc_start = result.find('📋 <i>') + len('📋 <i>')
        desc_end = result.find('</i>')
        description_in_result = result[desc_start:desc_end]
        self.assertLess(len(description_in_result), len(long_description))
        self.assertLessEqual(len(description_in_result), 300)

    def test_format_project_message_vacancy(self):
        """Тест форматирования сообщения о проекте (вакансия)"""
        # Подготовка
        project = {
            'title': 'Senior Python Developer',
            'description': 'Ищем опытного разработчика Python',
            'budget': 200000,
            'region': 'Москва',
            'type': 'vacancy',
            'technologies': ['Python', 'Django', 'PostgreSQL'],
            'url': 'https://example.com/vacancy/1'
        }

        # Выполнение
        result = self.personalization_engine.format_project_message(project)

        # Проверка
        self.assertIn('🆕 Вакансия', result)
        self.assertIn('💰 Бюджет: 200000 руб.', result)

    def test_get_personalized_notifications(self):
        """Тест получения персонализированных уведомлений"""
        # Подготовка
        projects = [
            {
                'title': 'Разработка Telegram бота на Python',
                'description': 'Требуется разработать бота для автоматизации задач',
                'budget': 3000,
                'region': 'Москва',
                'technologies': ['Python', 'Django'],
                'type': 'order',
                'url': 'https://example.com/project/1'
            }
        ]

        user_settings_1 = UserSettings(
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

        # Мокаем получение подписанных пользователей
        self.mock_user_settings_manager.get_subscribed_users = MagicMock(
            return_value=[user_settings_1]
        )

        # Мокаем фильтрацию
        self.mock_filter_engine.filter_projects = MagicMock(return_value=projects)

        # Мокаем форматирование сообщения
        formatted_message = "Новое предложение: Разработка Telegram бота на Python"
        self.personalization_engine.format_project_message = MagicMock(return_value=formatted_message)

        # Выполнение
        result = self.personalization_engine.get_personalized_notifications(projects)

        # Проверка
        self.assertEqual(len(result), 1)
        self.assertIn(123456, result)
        self.assertEqual(len(result[123456]), 1)
        self.assertEqual(result[123456][0], formatted_message)

    def test_get_personalized_notifications_no_matches(self):
        """Тест получения персонализированных уведомлений (нет совпадений)"""
        # Подготовка
        projects = [
            {
                'title': 'Верстка сайта',
                'description': 'Необходимо сверстать макет',
                'budget': 1500,
                'region': 'Санкт-Петербург',
                'technologies': ['HTML', 'CSS'],
                'type': 'order'
            }
        ]

        user_settings_1 = UserSettings(
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

        # Мокаем получение подписанных пользователей
        self.mock_user_settings_manager.get_subscribed_users = MagicMock(
            return_value=[user_settings_1]
        )

        # Мокаем фильтрацию (возвращаем пустой список)
        self.mock_filter_engine.filter_projects = MagicMock(return_value=[])

        # Выполнение
        result = self.personalization_engine.get_personalized_notifications(projects)

        # Проверка
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()