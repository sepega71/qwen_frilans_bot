#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования модуля сбора данных.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from datetime import datetime

from data_collector import DataCollector
from src.data_sources.fl_ru_collector import FlRuCollector
from src.data_sources.weblancer_collector import WeblancerCollector
from src.data_sources.freemarket_collector import FreemarketCollector
from src.data_sources.github_collector import GitHubCollector
from src.data_sources.telegram_collector import TelegramCollector


class TestDataCollector(unittest.TestCase):
    """Тесты для модуля сбора данных"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Создаем моки для всех сборщиков данных
        self.mock_fl_ru_collector = MagicMock(spec=FlRuCollector)
        self.mock_weblancer_collector = MagicMock(spec=WeblancerCollector)
        self.mock_freemarket_collector = MagicMock(spec=FreemarketCollector)
        self.mock_github_collector = MagicMock(spec=GitHubCollector)
        self.mock_telegram_collector = MagicMock(spec=TelegramCollector)

        # Создаем экземпляр DataCollector с моками
        self.collector = DataCollector()
        self.collector.fl_ru_collector = self.mock_fl_ru_collector
        self.collector.weblancer_collector = self.mock_weblancer_collector
        self.collector.freemarket_collector = self.mock_freemarket_collector
        self.collector.github_collector = self.mock_github_collector
        self.collector.telegram_collector = self.mock_telegram_collector

    @patch('data_collector.FlRuCollector')
    async def test_fetch_fl_ru_data(self, mock_fl_ru_collector_class):
        """Тест сбора данных с fl.ru"""
        # Подготовка
        mock_instance = AsyncMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Тестовый проект', 'description': 'Описание', 'budget': 1000}
        ])
        mock_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Тестовый проект',
            'description': 'Описание',
            'budget': 1000,
            'source': 'fl.ru'
        })
        mock_fl_ru_collector_class.return_value = mock_instance

        # Обновляем collector с новым экземпляром
        collector = DataCollector()
        collector.fl_ru_collector = mock_instance

        # Выполнение
        result = await collector.fetch_fl_ru_data()

        # Проверка
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Тестовый проект')
        self.assertEqual(result[0]['source'], 'fl.ru')
        mock_instance.fetch_projects.assert_called_once_with(method='rss')

    @patch('data_collector.WeblancerCollector')
    async def test_fetch_weblancer_data(self, mock_weblancer_collector_class):
        """Тест сбора данных с weblancer.net"""
        # Подготовка
        mock_instance = AsyncMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Тестовый проект', 'description': 'Описание', 'budget': 200}
        ])
        mock_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Тестовый проект',
            'description': 'Описание',
            'budget': 2000,
            'source': 'weblancer.net'
        })
        mock_weblancer_collector_class.return_value = mock_instance

        # Обновляем collector с новым экземпляром
        collector = DataCollector()
        collector.weblancer_collector = mock_instance

        # Выполнение
        result = await collector.fetch_weblancer_data()

        # Проверка
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Тестовый проект')
        self.assertEqual(result[0]['source'], 'weblancer.net')
        mock_instance.fetch_projects.assert_called_once_with(method='rss')

    @patch('data_collector.FreemarketCollector')
    async def test_fetch_freemarket_data(self, mock_freemarket_collector_class):
        """Тест сбора данных с freemarket.ru"""
        # Подготовка
        mock_instance = AsyncMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Тестовый проект', 'description': 'Описание', 'budget': 300}
        ])
        mock_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Тестовый проект',
            'description': 'Описание',
            'budget': 3000,
            'source': 'freemarket.ru'
        })
        mock_freemarket_collector_class.return_value = mock_instance

        # Обновляем collector с новым экземпляром
        collector = DataCollector()
        collector.freemarket_collector = mock_instance

        # Выполнение
        result = await collector.fetch_freemarket_data()

        # Проверка
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Тестовый проект')
        self.assertEqual(result[0]['source'], 'freemarket.ru')
        mock_instance.fetch_projects.assert_called_once()

    @patch('data_collector.GitHubCollector')
    async def test_fetch_github_data(self, mock_github_collector_class):
        """Тест сбора данных с GitHub"""
        # Подготовка
        mock_instance = AsyncMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.fetch_projects = AsyncMock(return_value=[
            {'title': 'Тестовый проект', 'description': 'Описание', 'budget': None}
        ])
        mock_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Тестовый проект',
            'description': 'Описание',
            'budget': None,
            'source': 'github'
        })
        mock_github_collector_class.return_value = mock_instance

        # Обновляем collector с новым экземпляром
        collector = DataCollector()
        collector.github_collector = mock_instance

        # Выполнение
        result = await collector.fetch_github_data()

        # Проверка
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Тестовый проект')
        self.assertEqual(result[0]['source'], 'github')
        mock_instance.fetch_projects.assert_called_once()

    @patch('data_collector.TelegramCollector')
    async def test_fetch_telegram_data(self, mock_telegram_collector_class):
        """Тест сбора данных из Telegram"""
        # Подготовка
        mock_instance = AsyncMock()
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_instance.initialize = AsyncMock()
        mock_instance.close = AsyncMock()
        mock_instance.collect_from_channels = AsyncMock(return_value=[
            {'title': 'Тестовый проект', 'description': 'Описание', 'budget': 5000}
        ])
        mock_instance.normalize_project_data = MagicMock(return_value={
            'title': 'Тестовый проект',
            'description': 'Описание',
            'budget': 5000,
            'source': 'telegram'
        })
        mock_telegram_collector_class.return_value = mock_instance

        # Обновляем collector с новым экземпляром
        collector = DataCollector()
        collector.telegram_collector = mock_instance

        # Выполнение
        result = await collector.collect_all_data()

        # Проверка
        # Должен содержать хотя бы один элемент из Telegram
        found_telegram_project = any(project['source'] == 'telegram' for project in result)
        self.assertTrue(found_telegram_project)
        mock_instance.collect_from_channels.assert_called_once()

    @patch('data_collector.FlRuCollector')
    @patch('data_collector.WeblancerCollector')
    @patch('data_collector.FreemarketCollector')
    @patch('data_collector.GitHubCollector')
    @patch('data_collector.TelegramCollector')
    async def test_collect_all_data(self, mock_telegram, mock_github, mock_freemarket, mock_weblancer, mock_flru):
        """Тест сбора данных из всех источников"""
        # Подготовка моков для всех источников
        mock_flru_instance = AsyncMock()
        mock_flru_instance.__aenter__ = AsyncMock(return_value=mock_flru_instance)
        mock_flru_instance.__aexit__ = AsyncMock(return_value=None)
        mock_flru_instance.fetch_projects = AsyncMock(return_value=[{'title': 'FL Project', 'budget': 1000}])
        mock_flru_instance.normalize_project_data = MagicMock(return_value={'title': 'FL Project', 'budget': 1000, 'source': 'fl.ru'})

        mock_weblancer_instance = AsyncMock()
        mock_weblancer_instance.__aenter__ = AsyncMock(return_value=mock_weblancer_instance)
        mock_weblancer_instance.__aexit__ = AsyncMock(return_value=None)
        mock_weblancer_instance.fetch_projects = AsyncMock(return_value=[{'title': 'Weblancer Project', 'budget': 2000}])
        mock_weblancer_instance.normalize_project_data = MagicMock(return_value={'title': 'Weblancer Project', 'budget': 2000, 'source': 'weblancer.net'})

        mock_freemarket_instance = AsyncMock()
        mock_freemarket_instance.__aenter__ = AsyncMock(return_value=mock_freemarket_instance)
        mock_freemarket_instance.__aexit__ = AsyncMock(return_value=None)
        mock_freemarket_instance.fetch_projects = AsyncMock(return_value=[{'title': 'Freemarket Project', 'budget': 3000}])
        mock_freemarket_instance.normalize_project_data = MagicMock(return_value={'title': 'Freemarket Project', 'budget': 3000, 'source': 'freemarket.ru'})

        mock_github_instance = AsyncMock()
        mock_github_instance.__aenter__ = AsyncMock(return_value=mock_github_instance)
        mock_github_instance.__aexit__ = AsyncMock(return_value=None)
        mock_github_instance.fetch_projects = AsyncMock(return_value=[{'title': 'GitHub Project', 'budget': None}])
        mock_github_instance.normalize_project_data = MagicMock(return_value={'title': 'GitHub Project', 'budget': None, 'source': 'github'})

        mock_telegram_instance = AsyncMock()
        mock_telegram_instance.__aenter__ = AsyncMock(return_value=mock_telegram_instance)
        mock_telegram_instance.__aexit__ = AsyncMock(return_value=None)
        mock_telegram_instance.initialize = AsyncMock()
        mock_telegram_instance.close = AsyncMock()
        mock_telegram_instance.collect_from_channels = AsyncMock(return_value=[{'title': 'Telegram Project', 'budget': 5000}])
        mock_telegram_instance.normalize_project_data = MagicMock(return_value={'title': 'Telegram Project', 'budget': 500, 'source': 'telegram'})

        # Настройка возвращаемых значений
        mock_flru.return_value = mock_flru_instance
        mock_weblancer.return_value = mock_weblancer_instance
        mock_freemarket.return_value = mock_freemarket_instance
        mock_github.return_value = mock_github_instance
        mock_telegram.return_value = mock_telegram_instance

        # Создаем новый экземпляр с моками
        collector = DataCollector()
        collector.fl_ru_collector = mock_flru_instance
        collector.weblancer_collector = mock_weblancer_instance
        collector.freemarket_collector = mock_freemarket_instance
        collector.github_collector = mock_github_instance
        collector.telegram_collector = mock_telegram_instance

        # Выполнение
        result = await collector.collect_all_data()

        # Проверка
        self.assertEqual(len(result), 5)  # 5 проектов из разных источников
        sources = [project['source'] for project in result]
        self.assertIn('fl.ru', sources)
        self.assertIn('weblancer.net', sources)
        self.assertIn('freemarket.ru', sources)
        self.assertIn('github', sources)
        self.assertIn('telegram', sources)

    def test_normalize_project_data(self):
        """Тест нормализации данных проекта"""
        # Подготовка
        raw_project = {
            'title': 'Тестовый проект',
            'description': 'Описание проекта',
            'budget': 1000,
            'region': 'Москва',
            'technologies': 'Python, Django',
            'url': 'https://example.com/project',
            'date': '2023-01-01T00:00',
            'source': 'test_source',
            'type': 'order',
            'external_id': '12345'
        }

        # Выполнение
        normalized = self.collector.normalize_project_data(raw_project)

        # Проверка
        self.assertEqual(normalized['title'], 'Тестовый проект')
        self.assertEqual(normalized['description'], 'Описание проекта')
        self.assertEqual(normalized['budget'], 1000)
        self.assertEqual(normalized['region'], 'Москва')
        self.assertEqual(normalized['url'], 'https://example.com/project')
        self.assertEqual(normalized['source'], 'test_source')
        self.assertEqual(normalized['type'], 'order')
        self.assertEqual(normalized['external_id'], '12345')
        self.assertIsInstance(normalized['technologies'], list)
        self.assertEqual(normalized['technologies'], ['Python, Django'])  # technologies остается строкой, т.к. не список

    def test_normalize_project_data_with_list_technologies(self):
        """Тест нормализации данных проекта с технологиями в виде списка"""
        # Подготовка
        raw_project = {
            'title': 'Тестовый проект',
            'description': 'Описание проекта',
            'budget': 1000,
            'region': 'Москва',
            'technologies': ['Python', 'Django'],
            'url': 'https://example.com/project',
            'date': '2023-01-01T00:00:00',
            'source': 'test_source',
            'type': 'order',
            'external_id': '12345'
        }

        # Выполнение
        normalized = self.collector.normalize_project_data(raw_project)

        # Проверка
        self.assertEqual(normalized['title'], 'Тестовый проект')
        self.assertEqual(normalized['description'], 'Описание проекта')
        self.assertEqual(normalized['budget'], 1000)
        self.assertEqual(normalized['region'], 'Москва')
        self.assertEqual(normalized['url'], 'https://example.com/project')
        self.assertEqual(normalized['source'], 'test_source')
        self.assertEqual(normalized['type'], 'order')
        self.assertEqual(normalized['external_id'], '12345')
        self.assertIsInstance(normalized['technologies'], list)
        self.assertEqual(normalized['technologies'], ['Python', 'Django'])


class TestDataSourceCollectors(unittest.TestCase):
    """Тесты для отдельных сборщиков данных"""

    @patch('src.data_sources.fl_ru_collector.requests.get')
    def test_fl_ru_collector_rss(self, mock_get):
        """Тест сборщика данных с fl.ru через RSS"""
        # Подготовка
        mock_response = MagicMock()
        mock_response.text = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
        <channel>
        <title>FL.RU - Проекты</title>
        <item>
        <title>Тестовый проект</title>
        <description>Описание тестового проекта</description>
        <link>https://www.fl.ru/projects/12345</link>
        <pubDate>Mon, 01 Jan 2023 00:00:00 +0000</pubDate>
        </item>
        </channel>
        </rss>'''
        mock_get.return_value = mock_response

        collector = FlRuCollector()
        projects = collector.fetch_projects(method='rss')

        # Проверка
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['title'], 'Тестовый проект')
        self.assertEqual(projects[0]['description'], 'Описание тестового проекта')
        self.assertEqual(projects[0]['url'], 'https://www.fl.ru/projects/12345')

    @patch('src.data_sources.weblancer_collector.requests.get')
    def test_weblancer_collector_rss(self, mock_get):
        """Тест сборщика данных с weblancer.net через RSS"""
        # Подготовка
        mock_response = MagicMock()
        mock_response.text = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
        <channel>
        <title>Weblancer - Проекты</title>
        <item>
        <title>Тестовый проект</title>
        <description>Описание тестового проекта</description>
        <link>https://www.weblancer.net/projects/12345</link>
        <pubDate>Mon, 01 Jan 2023 00:00:00 +0000</pubDate>
        </item>
        </channel>
        </rss>'''
        mock_get.return_value = mock_response

        collector = WeblancerCollector()
        projects = collector.fetch_projects(method='rss')

        # Проверка
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['title'], 'Тестовый проект')
        self.assertEqual(projects[0]['description'], 'Описание тестового проекта')
        self.assertEqual(projects[0]['url'], 'https://www.weblancer.net/projects/12345')

    @patch('src.data_sources.github_collector.requests.get')
    def test_github_collector(self, mock_get):
        """Тест сборщика данных с GitHub API"""
        # Подготовка
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                'id': 12345,
                'title': 'Тестовый проект',
                'body': 'Описание тестового проекта',
                'html_url': 'https://github.com/user/repo/issues/1',
                'created_at': '2023-01-01T00:00Z'
            }
        ]
        mock_get.return_value = mock_response

        collector = GitHubCollector(token='test_token')
        projects = collector.fetch_projects()

        # Проверка
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['title'], 'Тестовый проект')
        self.assertEqual(projects[0]['description'], 'Описание тестового проекта')
        self.assertEqual(projects[0]['url'], 'https://github.com/user/repo/issues/1')


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()