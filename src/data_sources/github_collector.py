#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль сбора данных с GitHub API
Реализует функциональность для получения open-source проектов и вакансий через GitHub API.
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging


class GitHubCollector:
    """
    Класс для сбора данных с GitHub API
    Поддерживает получение данных о репозиториях и вакансиях
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Инициализация сборщика данных с GitHub API
        
        Args:
            token: Токен для аутентификации в GitHub API (необязательно, но рекомендуется)
        """
        self.base_url = "https://api.github.com"
        self.token = token
        self.headers = {
            'User-Agent': 'Frilans-Bot/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        
        self.logger = logging.getLogger(__name__)
        self.session = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие асинхронной сессии"""
        if self.session:
            await self.session.close()
    
    async def search_repositories(self, query: str, sort: str = 'updated', order: str = 'desc', per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Поиск репозиториев по заданному запросу
        
        Args:
            query: Поисковый запрос
            sort: Поле для сортировки (default: 'updated')
            order: Порядок сортировки ('asc' или 'desc', default: 'desc')
            per_page: Количество результатов на страницу (max: 100)
            
        Returns:
            List[Dict[str, Any]]: Список репозиториев
        """
        if not self.session:
            raise RuntimeError("Collector не инициализирован. Используйте 'async with' для инициализации.")
        
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': min(per_page, 10)  # GitHub API ограничивает максимум 100 результатов на страницу
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 20:
                    data = await response.json()
                    return data.get('items', [])
                else:
                    self.logger.error(f"Ошибка при поиске репозиториев: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Ошибка при поиске репозиториев: {e}")
            return []
    
    async def search_issues(self, query: str, sort: str = 'updated', order: str = 'desc', per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Поиск issues по заданному запросу (может использоваться для поиска вакансий и задач)
        
        Args:
            query: Поисковый запрос
            sort: Поле для сортировки (default: 'updated')
            order: Порядок сортировки ('asc' или 'desc', default: 'desc')
            per_page: Количество результатов на страницу (max: 100)
            
        Returns:
            List[Dict[str, Any]]: Список issues
        """
        if not self.session:
            raise RuntimeError("Collector не инициализирован. Используйте 'async with' для инициализации.")
        
        url = f"{self.base_url}/search/issues"
        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': min(per_page, 10)  # GitHub API ограничивает максимум 100 результатов на страницу
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                else:
                    self.logger.error(f"Ошибка при поиске issues: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Ошибка при поиске issues: {e}")
            return []
    
    async def get_repo_details(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Получение деталей репозитория
        
        Args:
            owner: Владелец репозитория
            repo: Название репозитория
            
        Returns:
            Optional[Dict[str, Any]]: Детали репозитория
        """
        if not self.session:
            raise RuntimeError("Collector не инициализирован. Используйте 'async with' для инициализации.")
        
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Ошибка при получении деталей репозитория: {response.status}")
                    return None
        except Exception as e:
            self.logger.error(f"Ошибка при получении деталей репозитория: {e}")
            return None
    
    async def get_repo_contributors(self, owner: str, repo: str, per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Получение списка контрибьюторов репозитория
        
        Args:
            owner: Владелец репозитория
            repo: Название репозитория
            per_page: Количество результатов на страницу (max: 100)
            
        Returns:
            List[Dict[str, Any]]: Список контрибьюторов
        """
        if not self.session:
            raise RuntimeError("Collector не инициализирован. Используйте 'async with' для инициализации.")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {
            'per_page': min(per_page, 100)
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Ошибка при получении контрибьюторов: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении контрибьюторов: {e}")
            return []
    
    async def fetch_projects(self, search_query: str = "freelance OR outsourcing OR vacancy") -> List[Dict[str, Any]]:
        """
        Основной метод для получения проектов с GitHub
        
        Args:
            search_query: Поисковый запрос для поиска релевантных проектов
            
        Returns:
            List[Dict[str, Any]]: Список проектов
        """
        projects = []
        
        try:
            # Сначала ищем репозитории
            repos = await self.search_repositories(search_query)
            
            for repo in repos:
                project = {
                    'title': repo.get('name', ''),
                    'description': repo.get('description', ''),
                    'url': repo.get('html_url', ''),
                    'date': repo.get('updated_at', datetime.now().isoformat()),
                    'source': 'github.com',
                    'type': 'vacancy',  # Для open-source проектов это может быть вакансия на контрибьюцию
                    'external_id': f"github_{repo.get('id', '')}",
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'language': repo.get('language', ''),
                    'topics': repo.get('topics', []),
                    'owner': repo.get('owner', {}).get('login', '')
                }
                
                projects.append(project)
            
            # Затем ищем issues (которые могут содержать вакансии или задачи)
            issues = await self.search_issues(search_query)
            
            for issue in issues:
                # Пропускаем pull requests (они помечены как pull_request)
                if 'pull_request' in issue:
                    continue
                
                project = {
                    'title': issue.get('title', ''),
                    'description': issue.get('body', ''),
                    'url': issue.get('html_url', ''),
                    'date': issue.get('updated_at', datetime.now().isoformat()),
                    'source': 'github.com',
                    'type': 'vacancy',  # Issues могут содержать вакансии или задачи
                    'external_id': f"github_issue_{issue.get('id', '')}",
                    'state': issue.get('state', ''),
                    'labels': [label.get('name', '') for label in issue.get('labels', [])],
                    'repository': issue.get('repository_url', '').split('/')[-1],
                    'owner': issue.get('user', {}).get('login', '')
                }
                
                projects.append(project)
        
        except Exception as e:
            self.logger.error(f"Ошибка при сборе данных с GitHub: {e}")
        
        return projects
    
    def normalize_project_data(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализация данных проекта к единому формату
        
        Args:
            project: Проект в формате GitHub
            
        Returns:
            Dict[str, Any]: Нормализованный проект
        """
        normalized = {
            'title': project.get('title', ''),
            'description': project.get('description', ''),
            'budget': project.get('budget'),  # GitHub обычно не содержит информации о бюджете
            'region': project.get('region', 'Удаленная работа'),
            'technologies': project.get('topics', []) + ([project.get('language')] if project.get('language') else []),
            'url': project.get('url', ''),
            'date': project.get('date', datetime.now().isoformat()),
            'source': project.get('source', 'github.com'),
            'type': project.get('type', 'vacancy'),
            'external_id': project.get('external_id', ''),
        }
        
        # Убираем дубликаты технологий и приводим к нижнему регистру
        if normalized['technologies']:
            normalized['technologies'] = list(set(tech.lower() for tech in normalized['technologies'] if tech))
        
        # Убираем пустые значения
        if not normalized['budget']:
            normalized['budget'] = None
        if not normalized['region']:
            normalized['region'] = 'Удаленная работа'
        
        return normalized