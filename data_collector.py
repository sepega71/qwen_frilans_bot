#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль сбора данных из различных источников.
Сканирует API, веб-сайты и телеграм-каналы для извлечения информации о заказах и вакансиях.
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from bs4 import BeautifulSoup

# Импорты для новых источников данных
from src.data_sources.fl_ru_collector import FlRuCollector
from src.data_sources.weblancer_collector import WeblancerCollector
from src.data_sources.freemarket_collector import FreemarketCollector
from src.data_sources.github_collector import GitHubCollector
from src.data_sources.telegram_collector import TelegramCollector


class DataCollector:
    """
    Класс для сбора данных из различных источников.
    """
    
    def __init__(self, telegram_api_id: str = None, telegram_api_hash: str = None, telegram_phone: str = None, github_token: str = None):
        """Инициализация сборщика данных"""
        self.fl_ru_collector = FlRuCollector()
        self.weblancer_collector = WeblancerCollector()
        self.freemarket_collector = FreemarketCollector()
        self.github_collector = GitHubCollector(token=github_token)
        
        # Инициализация TelegramCollector только если предоставлены учетные данные
        if telegram_api_id and telegram_api_hash and telegram_phone:
            self.telegram_collector = TelegramCollector(
                api_id=telegram_api_id,
                api_hash=telegram_api_hash,
                phone=telegram_phone
            )
        else:
            self.telegram_collector = None
    
    async def fetch_fl_ru_data(self) -> List[Dict[str, Any]]:
        """
        Сбор данных с fl.ru
        
        Returns:
            List[Dict[str, Any]]: Список проектов с fl.ru
        """
        async with self.fl_ru_collector as collector:
            projects = await collector.fetch_projects(method='rss')
            # Нормализуем данные
            normalized_projects = [collector.normalize_project_data(project) for project in projects]
            return normalized_projects
    
    async def fetch_weblancer_data(self) -> List[Dict[str, Any]]:
        """
        Сбор данных с weblancer.net
        
        Returns:
            List[Dict[str, Any]]: Список проектов с weblancer.net
        """
        async with self.weblancer_collector as collector:
            projects = await collector.fetch_projects(method='rss')
            # Нормализуем данные
            normalized_projects = [collector.normalize_project_data(project) for project in projects]
            return normalized_projects
    
    async def fetch_freemarket_data(self) -> List[Dict[str, Any]]:
        """
        Сбор данных с freemarket.ru
        
        Returns:
            List[Dict[str, Any]]: Список проектов с freemarket.ru
        """
        async with self.freemarket_collector as collector:
            projects = await collector.fetch_projects()
            # Нормализуем данные
            normalized_projects = [collector.normalize_project_data(project) for project in projects]
            return normalized_projects
    
    async def fetch_github_data(self) -> List[Dict[str, Any]]:
        """
        Сбор данных с GitHub API для open-source проектов
        
        Returns:
            List[Dict[str, Any]]: Список проектов с GitHub
        """
        async with self.github_collector as collector:
            projects = await collector.fetch_projects()
            # Нормализуем данные
            normalized_projects = [collector.normalize_project_data(project) for project in projects]
            return normalized_projects
    
    async def collect_all_data(self) -> List[Dict[str, Any]]:
        """
        Сбор данных из всех источников
        
        Returns:
            List[Dict[str, Any]]: Объединенный список проектов из всех источников
        """
        all_projects = []
        
        # Сбор данных из всех источников
        fl_projects = await self.fetch_fl_ru_data()
        weblancer_projects = await self.fetch_weblancer_data()
        freemarket_projects = await self.fetch_freemarket_data()
        github_projects = await self.fetch_github_data()
        
        # Объединяем все проекты
        all_projects.extend(fl_projects)
        all_projects.extend(weblancer_projects)
        all_projects.extend(freemarket_projects)
        all_projects.extend(github_projects)
        
        # Если доступен TelegramCollector, добавляем данные из Telegram
        if self.telegram_collector:
            try:
                # Инициализируем клиент
                await self.telegram_collector.initialize()
                
                # Пример: сбор из определенных каналов
                telegram_channels = [
                    'freelance_tasks',  # Пример канала с заданиями для фрилансеров
                    'it_vacancies',     # Пример канала с IT вакансиями
                    'webdev_jobs'       # Пример канала с веб-разработкой
                ]
                
                telegram_projects = await self.telegram_collector.collect_from_channels(
                    telegram_channels,
                    limit=10
                )
                
                # Нормализуем данные
                for project in telegram_projects:
                    normalized_project = self.telegram_collector.normalize_project_data(project)
                    all_projects.append(normalized_project)
            except Exception as e:
                print(f"Ошибка при сборе данных из Telegram: {e}")
            finally:
                # Закрываем клиент
                if self.telegram_collector:
                    await self.telegram_collector.close()
        
        return all_projects
    
    def normalize_project_data(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализация данных проекта к единому формату
        
        Args:
            project: Проект в произвольном формате
            
        Returns:
            Dict[str, Any]: Проект в нормализованном формате
        """
        normalized = {
            'title': project.get('title', ''),
            'description': project.get('description', ''),
            'budget': project.get('budget'),
            'region': project.get('region', ''),
            'technologies': project.get('technologies', []),
            'url': project.get('url', ''),
            'date': project.get('date', datetime.now().isoformat()),
            'source': project.get('source', ''),
            'type': project.get('type', 'order'),  # 'order' или 'vacancy'
            'external_id': project.get('external_id', ''),  # Уникальный ID в источнике
        }
        
        # Приведение технологий к списку строк, если это одна строка
        if isinstance(normalized['technologies'], str):
            normalized['technologies'] = [normalized['technologies']]
        
        return normalized