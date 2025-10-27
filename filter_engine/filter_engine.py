#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Базовый модуль фильтрации заказов и вакансий.
Содержит основные фильтры, которые используются в боте.
"""

from typing import Dict, List, Any, Optional
from .advanced_filter import AdvancedFilterEngine


class FilterEngine:
    """
    Класс для фильтрации проектов по основным критериям.
    """
    
    def __init__(self):
        """Инициализация движка фильтрации"""
        self.advanced_filter = AdvancedFilterEngine()
    
    def filter_projects(self, projects: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Фильтрует список проектов по заданным критериям
        
        Args:
            projects: Список проектов для фильтрации
            filters: Словарь фильтров
            
        Returns:
            Список отфильтрованных проектов
        """
        filtered_projects = []
        
        for project in projects:
            if self._matches_filters(project, filters):
                filtered_projects.append(project)
        
        return filtered_projects
    
    def _matches_filters(self, project: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Проверяет, соответствует ли проект всем фильтрам
        
        Args:
            project: Данные проекта
            filters: Словарь фильтров
            
        Returns:
            bool: Соответствует ли проект фильтрам
        """
        # Проверяем минимальную цену
        min_price = filters.get('min_price')
        if min_price is not None:
            price = self._extract_price(project.get('price', '0'))
            if price < min_price:
                return False
        
        # Проверяем максимальную цену
        max_price = filters.get('max_price')
        if max_price is not None:
            price = self._extract_price(project.get('price', '0'))
            if price > max_price:
                return False
        
        # Проверяем ключевые слова в названии и описании
        keywords = filters.get('keywords', [])
        if keywords:
            if not self._matches_keywords(project, keywords):
                return False
        
        # Проверяем теги
        tags = filters.get('tags', [])
        if tags:
            project_tags = project.get('tags', [])
            if not any(tag in project_tags for tag in tags):
                return False
        
        # Проверяем язык общения
        language = filters.get('language')
        if language:
            project_language = project.get('language', 'ru')
            if project_language != language:
                return False
        
        # Проверяем дополнительные фильтры с помощью расширенного движка
        if not self.advanced_filter.matches_deadline(project, filters.get('max_deadline_days')):
            return False
        
        if not self.advanced_filter.matches_experience_level(project, filters.get('experience_level')):
            return False
        
        if not self.advanced_filter.matches_payment_type(project, filters.get('payment_type')):
            return False
        
        if 'complex_keywords' in filters:
            if not self.advanced_filter.matches_complex_keywords(project, filters['complex_keywords']):
                return False
        
        # Проверяем регион, если он указан в проекте и фильтрах
        regions = filters.get('regions', [])
        if regions:
            project_region = project.get('region', '').lower()
            if project_region and not any(region.lower() in project_region for region in regions):
                return False
        
        # Проверяем типы проектов
        project_types = filters.get('project_types', [])
        if project_types:
            project_type = project.get('type', '').lower()
            if project_type and project_type not in project_types:
                return False
        
        return True
    
    def _extract_price(self, price_str: str) -> float:
        """
        Извлекает числовое значение цены из строки
        
        Args:
            price_str: Строка с ценой
            
        Returns:
            Числовое значение цены
        """
        import re
        # Ищем все числа в строке и возвращаем первое
        numbers = re.findall(r'\d+\.?\d*', str(price_str))
        if numbers:
            return float(numbers[0])
        return 0.0
    
    def _matches_keywords(self, project: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Проверяет, содержатся ли ключевые слова в проекте
        
        Args:
            project: Данные проекта
            keywords: Список ключевых слов для поиска
            
        Returns:
            bool: Содержатся ли ключевые слова в проекте
        """
        title = project.get('title', '').lower()
        description = project.get('description', '').lower()
        
        for keyword in keywords:
            keyword = keyword.lower().strip()
            if keyword not in title and keyword not in description:
                return False
        
        return True