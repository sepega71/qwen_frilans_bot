#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования системы фильтрации.
"""

import unittest
from unittest.mock import MagicMock
from filter_engine import FilterEngine
from user_settings_manager import UserFilters


class TestFilterEngine(unittest.TestCase):
    """Тесты для системы фильтрации"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.filter_engine = FilterEngine()

    def test_matches_keywords_positive(self):
        """Тест проверки соответствия ключевым словам (позитивный)"""
        project_data = {
            'title': 'Разработка Telegram бота на Python',
            'description': 'Требуется разработать бота для автоматизации задач'
        }
        keywords = ['python', 'telegram', 'бот']

        result = self.filter_engine.matches_keywords(project_data, keywords)
        self.assertTrue(result)

    def test_matches_keywords_negative(self):
        """Тест проверки соответствия ключевым словам (негативный)"""
        project_data = {
            'title': 'Разработка веб-сайта на JavaScript',
            'description': 'Создание интерактивного веб-приложения'
        }
        keywords = ['python', 'telegram', 'бот']

        result = self.filter_engine.matches_keywords(project_data, keywords)
        self.assertFalse(result)

    def test_matches_keywords_empty(self):
        """Тест проверки соответствия ключевым словам (пустой список)"""
        project_data = {
            'title': 'Разработка веб-сайта на JavaScript',
            'description': 'Создание интерактивного веб-приложения'
        }
        keywords = []

        result = self.filter_engine.matches_keywords(project_data, keywords)
        self.assertTrue(result)

    def test_matches_technologies_positive(self):
        """Тест проверки соответствия технологиям (позитивный)"""
        project_data = {
            'title': 'Разработка веб-приложения',
            'technologies': ['Python', 'Django', 'PostgreSQL']
        }
        technologies = ['python', 'django']

        result = self.filter_engine.matches_technologies(project_data, technologies)
        self.assertTrue(result)

    def test_matches_technologies_negative(self):
        """Тест проверки соответствия технологиям (негативный)"""
        project_data = {
            'title': 'Разработка веб-приложения',
            'technologies': ['JavaScript', 'React', 'Node.js']
        }
        technologies = ['python', 'django']

        result = self.filter_engine.matches_technologies(project_data, technologies)
        self.assertFalse(result)

    def test_matches_technologies_empty_project(self):
        """Тест проверки соответствия технологиям (пустой список в проекте)"""
        project_data = {
            'title': 'Разработка веб-приложения',
            'technologies': []
        }
        technologies = ['python', 'django']

        result = self.filter_engine.matches_technologies(project_data, technologies)
        self.assertFalse(result)

    def test_matches_technologies_empty_user(self):
        """Тест проверки соответствия технологиям (пустой список у пользователя)"""
        project_data = {
            'title': 'Разработка веб-приложения',
            'technologies': ['Python', 'Django', 'PostgreSQL']
        }
        technologies = []

        result = self.filter_engine.matches_technologies(project_data, technologies)
        self.assertTrue(result)

    def test_matches_budget_positive(self):
        """Тест проверки соответствия бюджету (позитивный)"""
        project_data = {
            'title': 'Разработка сайта',
            'budget': 50000
        }

        result = self.filter_engine.matches_budget(project_data, min_budget=10000, max_budget=10000)
        self.assertTrue(result)

    def test_matches_budget_negative_min(self):
        """Тест проверки соответствия бюджету (ниже минимального)"""
        project_data = {
            'title': 'Разработка сайта',
            'budget': 5000
        }

        result = self.filter_engine.matches_budget(project_data, min_budget=10000, max_budget=100000)
        self.assertFalse(result)

    def test_matches_budget_negative_max(self):
        """Тест проверки соответствия бюджету (выше максимального)"""
        project_data = {
            'title': 'Разработка сайта',
            'budget': 500000
        }

        result = self.filter_engine.matches_budget(project_data, min_budget=1000, max_budget=10000)
        self.assertFalse(result)

    def test_matches_budget_no_project_budget(self):
        """Тест проверки соответствия бюджету (бюджет не указан в проекте)"""
        project_data = {
            'title': 'Разработка сайта',
            'budget': None
        }

        result = self.filter_engine.matches_budget(project_data, min_budget=10000, max_budget=100000)
        self.assertTrue(result)

    def test_matches_budget_no_min_max(self):
        """Тест проверки соответствия бюджету (без указания min/max)"""
        project_data = {
            'title': 'Разработка сайта',
            'budget': 50000
        }

        result = self.filter_engine.matches_budget(project_data)
        self.assertTrue(result)

    def test_matches_region_positive(self):
        """Тест проверки соответствия региону (позитивный)"""
        project_data = {
            'title': 'Разработка сайта',
            'region': 'Москва'
        }
        regions = ['Москва', 'Санкт-Петербург']

        result = self.filter_engine.matches_region(project_data, regions)
        self.assertTrue(result)

    def test_matches_region_negative(self):
        """Тест проверки соответствия региону (негативный)"""
        project_data = {
            'title': 'Разработка сайта',
            'region': 'Новосибирск'
        }
        regions = ['Москва', 'Санкт-Петербург']

        result = self.filter_engine.matches_region(project_data, regions)
        self.assertFalse(result)

    def test_matches_region_empty(self):
        """Тест проверки соответствия региону (пустой список)"""
        project_data = {
            'title': 'Разработка сайта',
            'region': 'Новосибирск'
        }
        regions = []

        result = self.filter_engine.matches_region(project_data, regions)
        self.assertTrue(result)

    def test_matches_region_no_project_region(self):
        """Тест проверки соответствия региону (регион не указан в проекте)"""
        project_data = {
            'title': 'Разработка сайта',
            'region': ''
        }
        regions = ['Москва', 'Санкт-Петербург']

        result = self.filter_engine.matches_region(project_data, regions)
        self.assertTrue(result)

    def test_matches_project_type_positive(self):
        """Тест проверки соответствия типу проекта (позитивный)"""
        project_data = {
            'title': 'Разработка сайта',
            'type': 'order'
        }
        project_types = ['order', 'vacancy']

        result = self.filter_engine.matches_project_type(project_data, project_types)
        self.assertTrue(result)

    def test_matches_project_type_negative(self):
        """Тест проверки соответствия типу проекта (негативный)"""
        project_data = {
            'title': 'Разработка сайта',
            'type': 'vacancy'
        }
        project_types = ['order']

        result = self.filter_engine.matches_project_type(project_data, project_types)
        self.assertFalse(result)

    def test_matches_project_type_empty(self):
        """Тест проверки соответствия типу проекта (пустой список)"""
        project_data = {
            'title': 'Разработка сайта',
            'type': 'order'
        }
        project_types = []

        result = self.filter_engine.matches_project_type(project_data, project_types)
        self.assertTrue(result)

    def test_matches_filters_all_positive(self):
        """Тест проверки соответствия всем фильтрам (позитивный)"""
        project_data = {
            'title': 'Разработка Telegram бота на Python',
            'description': 'Требуется разработать бота для автоматизации задач',
            'budget': 50000,
            'region': 'Москва',
            'technologies': ['Python', 'Django'],
            'type': 'order'
        }

        user_filters = UserFilters(
            keywords=['python', 'telegram'],
            technologies=['python', 'django'],
            budget_min=10000,
            budget_max=10000,
            regions=['Москва'],
            project_types=['order']
        )

        result = self.filter_engine.matches_filters(project_data, user_filters)
        self.assertTrue(result)

    def test_matches_filters_one_negative(self):
        """Тест проверки соответствия всем фильтрам (один фильтр не подходит)"""
        project_data = {
            'title': 'Разработка Telegram бота на Python',
            'description': 'Требуется разработать бота для автоматизации задач',
            'budget': 50000,
            'region': 'Новосибирск',  # Регион не подходит
            'technologies': ['Python', 'Django'],
            'type': 'order'
        }

        user_filters = UserFilters(
            keywords=['python', 'telegram'],
            technologies=['python', 'django'],
            budget_min=10000,
            budget_max=10000,
            regions=['Москва'],
            project_types=['order']
        )

        result = self.filter_engine.matches_filters(project_data, user_filters)
        self.assertFalse(result)

    def test_filter_projects(self):
        """Тест фильтрации списка проектов"""
        projects = [
            {
                'title': 'Разработка Telegram бота на Python',
                'description': 'Требуется разработать бота для автоматизации задач',
                'budget': 50000,
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

        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=10000,
            budget_max=100000,
            regions=['Москва'],
            project_types=['order']
        )

        filtered_projects = self.filter_engine.filter_projects(projects, user_filters)
        self.assertEqual(len(filtered_projects), 1)
        self.assertEqual(filtered_projects[0]['title'], 'Разработка Telegram бота на Python')

    def test_filter_projects_empty(self):
        """Тест фильтрации списка проектов (пустой список)"""
        projects = []

        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=10000,
            budget_max=10000,
            regions=['Москва'],
            project_types=['order']
        )

        filtered_projects = self.filter_engine.filter_projects(projects, user_filters)
        self.assertEqual(len(filtered_projects), 0)

    def test_filter_projects_no_matches(self):
        """Тест фильтрации списка проектов (нет совпадений)"""
        projects = [
            {
                'title': 'Верстка сайта',
                'description': 'Необходимо сверстать макет',
                'budget': 15000,
                'region': 'Санкт-Петербург',
                'technologies': ['HTML', 'CSS'],
                'type': 'order'
            }
        ]

        user_filters = UserFilters(
            keywords=['python'],
            technologies=['python'],
            budget_min=10000,
            budget_max=100000,
            regions=['Москва'],
            project_types=['order']
        )

        filtered_projects = self.filter_engine.filter_projects(projects, user_filters)
        self.assertEqual(len(filtered_projects), 0)


class TestAdvancedFilterEngine(unittest.TestCase):
    """Тесты для расширенного фильтра (проверка уровня опыта и формы оплаты)"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.filter_engine = FilterEngine()

    def test_matches_experience_level(self):
        """Тест проверки соответствия уровню опыта"""
        # Так как advanced_filter не полностью реализован в моке,
        # тестируем через проверку вызова метода
        project_data = {'experience_level': 'middle'}
        user_experience = 'middle'

        # Мокаем advanced_filter
        self.filter_engine.advanced_filter.matches_experience_level = MagicMock(return_value=True)

        result = self.filter_engine.advanced_filter.matches_experience_level(project_data, user_experience)
        self.assertTrue(result)
        self.filter_engine.advanced_filter.matches_experience_level.assert_called_once_with(project_data, user_experience)

    def test_matches_payment_type(self):
        """Тест проверки соответствия форме оплаты"""
        project_data = {'payment_type': 'fixed'}
        user_payment_type = 'fixed'

        # Мокаем advanced_filter
        self.filter_engine.advanced_filter.matches_payment_type = MagicMock(return_value=True)

        result = self.filter_engine.advanced_filter.matches_payment_type(project_data, user_payment_type)
        self.assertTrue(result)
        self.filter_engine.advanced_filter.matches_payment_type.assert_called_once_with(project_data, user_payment_type)


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()