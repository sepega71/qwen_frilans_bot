#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль сбора данных с weblancer.net
Реализует функциональность для получения проектов с weblancer.net через RSS и веб-скрапинг.
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from bs4 import BeautifulSoup
import logging
import time


class WeblancerCollector:
    """
    Класс для сбора данных с weblancer.net
    Поддерживает получение данных через RSS и веб-скрапинг
    """
    
    def __init__(self):
        """Инициализация сборщика данных с weblancer.net"""
        self.base_url = "https://www.weblancer.net"
        self.rss_url = "https://www.weblancer.net/rss/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
        # Для асинхронных запросов
        self.aiohttp_session = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        self.aiohttp_session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие асинхронной сессии"""
        if self.aiohttp_session:
            await self.aiohttp_session.close()
    
    async def fetch_projects_rss(self) -> List[Dict[str, Any]]:
        """
        Сбор проектов с weblancer.net через RSS
        
        Returns:
            List[Dict[str, Any]]: Список проектов с weblancer.net
        """
        projects = []
        try:
            if not self.aiohttp_session:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.rss_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            projects = self._parse_rss_content(content)
            else:
                async with self.aiohttp_session.get(self.rss_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        projects = self._parse_rss_content(content)
        except Exception as e:
            self.logger.error(f"Ошибка при сборе данных с weblancer.net через RSS: {e}")
        
        return projects
    
    def _parse_rss_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Парсинг RSS-контента weblancer.net
        
        Args:
            content: Содержимое RSS-ленты
            
        Returns:
            List[Dict[str, Any]]: Список проектов
        """
        projects = []
        
        try:
            # Находим все элементы <item>
            items = content.split('<item>')
            for item in items[1:]:  # Пропускаем первый элемент до <item>
                project = {}
                
                # Извлекаем заголовок
                title_match = re.search(r'<title>(.*?)</title>', item)
                if title_match:
                    project['title'] = title_match.group(1).strip()
                
                # Извлекаем описание
                desc_match = re.search(r'<description>(.*?)</description>', item)
                if desc_match:
                    description = desc_match.group(1)
                    # Извлекаем только текст без HTML-тегов
                    soup = BeautifulSoup(description, 'html.parser')
                    project['description'] = soup.get_text().strip()
                
                # Извлекаем ссылку
                link_match = re.search(r'<link>(.*?)</link>', item)
                if link_match:
                    project['url'] = link_match.group(1).strip()
                
                # Извлекаем дату
                date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if date_match:
                    project['date'] = date_match.group(1).strip()
                
                # Извлекаем категории (если есть)
                category_match = re.search(r'<category>(.*?)</category>', item)
                if category_match:
                    project['category'] = category_match.group(1).strip()
                
                if project:  # Если есть хотя бы один элемент
                    project['source'] = 'weblancer.net'
                    project['type'] = 'order'  # weblancer в основном для заказов
                    project['external_id'] = self._extract_external_id(project.get('url', ''))
                    projects.append(project)
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге RSS-контента weblancer.net: {e}")
        
        return projects
    
    def _extract_external_id(self, url: str) -> str:
        """
        Извлечение внешнего ID из URL
        
        Args:
            url: URL проекта
            
        Returns:
            str: Внешний ID проекта
        """
        # Извлекаем ID из URL (последнее число в URL)
        match = re.search(r'/projects/(\d+)', url)
        if match:
            return f"weblancer_{match.group(1)}"
        return url  # Возвращаем URL как ID, если не удалось извлечь
    
    async def fetch_projects_web(self, max_pages: int = 3) -> List[Dict[str, Any]]:
        """
        Сбор проектов с weblancer.net через веб-скрапинг
        
        Args:
            max_pages: Максимальное количество страниц для скрапинга
            
        Returns:
            List[Dict[str, Any]]: Список проектов с weblancer.net
        """
        projects = []
        
        try:
            # Основная страница с проектами
            url = f"{self.base_url}/projects/"
            
            for page_num in range(1, max_pages + 1):
                page_url = f"{url}?page={page_num}"
                
                # Делаем паузу между запросами, чтобы не спамить
                time.sleep(1)
                
                response = self.session.get(page_url)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Находим элементы с проектами (адаптировать под актуальную структуру сайта)
                project_elements = soup.find_all('div', class_='project')
                
                for element in project_elements:
                    project = self._parse_project_element(element)
                    if project:
                        projects.append(project)
                
                # Если на странице нет проектов, выходим
                if not project_elements:
                    break
        
        except Exception as e:
            self.logger.error(f"Ошибка при сборе данных с weblancer.net через веб-скрапинг: {e}")
        
        return projects
    
    def _parse_project_element(self, element) -> Optional[Dict[str, Any]]:
        """
        Парсинг отдельного элемента проекта
        
        Args:
            element: HTML-элемент проекта
            
        Returns:
            Optional[Dict[str, Any]]: Данные проекта или None
        """
        project = {}
        
        try:
            # Извлекаем заголовок
            title_elem = element.find('h3', class_='project-title')
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    project['title'] = title_link.get_text(strip=True)
                    project['url'] = self.base_url + title_link.get('href', '')
                    project['external_id'] = self._extract_external_id(project['url'])
            
            # Извлекаем описание
            desc_elem = element.find('div', class_='project-description')
            if desc_elem:
                project['description'] = desc_elem.get_text(strip=True)
            
            # Извлекаем бюджет
            budget_elem = element.find('span', class_='project-budget')
            if budget_elem:
                budget_text = budget_elem.get_text(strip=True)
                # Извлекаем числовое значение бюджета
                budget_match = re.search(r'[\d\s]+', budget_text.replace(' ', ''))
                if budget_match:
                    project['budget'] = int(budget_match.group(0))
            
            # Извлекаем дату
            date_elem = element.find('time')
            if date_elem:
                project['date'] = date_elem.get('datetime', datetime.now().isoformat())
            
            # Извлекаем категории/навыки
            skills_elem = element.find('div', class_='project-skills')
            if skills_elem:
                skill_tags = skills_elem.find_all('a', class_='skill-tag')
                project['technologies'] = [tag.get_text(strip=True) for tag in skill_tags]
            
            if project:
                project['source'] = 'weblancer.net'
                project['type'] = 'order'
                return project
        except Exception as e:
            self.logger.error(f"Ошибка при парсинге элемента проекта weblancer.net: {e}")
        
        return None
    
    async def fetch_projects(self, method: str = 'rss') -> List[Dict[str, Any]]:
        """
        Основной метод для получения проектов с weblancer.net
        
        Args:
            method: Метод получения данных ('rss' или 'web')
            
        Returns:
            List[Dict[str, Any]]: Список проектов
        """
        if method == 'rss':
            return await self.fetch_projects_rss()
        elif method == 'web':
            return await self.fetch_projects_web()
        else:
            raise ValueError("Метод должен быть 'rss' или 'web'")
    
    def normalize_project_data(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализация данных проекта к единому формату
        
        Args:
            project: Проект в формате weblancer.net
            
        Returns:
            Dict[str, Any]: Нормализованный проект
        """
        normalized = {
            'title': project.get('title', ''),
            'description': project.get('description', ''),
            'budget': project.get('budget'),
            'region': project.get('region', ''),
            'technologies': project.get('technologies', []),
            'url': project.get('url', ''),
            'date': project.get('date', datetime.now().isoformat()),
            'source': project.get('source', 'weblancer.net'),
            'type': project.get('type', 'order'),
            'external_id': project.get('external_id', ''),
        }
        
        # Приведение технологий к списку строк, если это одна строка
        if isinstance(normalized['technologies'], str):
            normalized['technologies'] = [normalized['technologies']]
        
        return normalized