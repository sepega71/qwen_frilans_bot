#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенный модуль фильтрации заказов и вакансий.
Содержит дополнительные фильтры, которые могут потребовать сложной логики.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re


class AdvancedFilterEngine:
    """
    Класс для расширенной фильтрации проектов по сложным критериям.
    """
    
    def __init__(self):
        """Инициализация расширенного движка фильтрации"""
        pass
    
    def matches_deadline(self, project_data: Dict[str, Any], max_deadline_days: Optional[int] = None) -> bool:
        """
        Проверяет, соответствует ли проект срокам выполнения
        
        Args:
            project_data: Данные проекта
            max_deadline_days: Максимальное количество дней до дедлайна
            
        Returns:
            bool: Соответствует ли проект срокам выполнения
        """
        if max_deadline_days is None:
            return True
            
        deadline_str = project_data.get('deadline')
        if deadline_str:
            try:
                # Пытаемся распознать формат даты
                deadline = self._parse_date(deadline_str)
                if deadline:
                    current_time = datetime.now()
                    delta = (deadline - current_time).days
                    return delta <= max_deadline_days
            except ValueError:
                pass  # Если формат даты неправильный, пропускаем проверку
        
        # Если дедлайн не указан в проекте, считаем, что он подходит
        return True
    
    def matches_experience_level(self, project_data: Dict[str, Any], experience_level: Optional[str] = None) -> bool:
        """
        Проверяет, соответствует ли проект уровню опыта
        
        Args:
            project_data: Данные проекта
            experience_level: Уровень опыта ('junior', 'middle', 'senior', 'expert')
            
        Returns:
            bool: Соответствует ли проект уровню опыта
        """
        if not experience_level:
            return True
            
        # Временная реализация - ищем уровень опыта в описании проекта
        description = project_data.get('description', '').lower()
        
        # Определяем ключевые слова для каждого уровня
        level_keywords = {
            'junior': ['junior', 'начинающ', 'стажер', 'обучени', 'first', 'entry'],
            'middle': ['middle', 'средний', 'intermediate', 'опытный'],
            'senior': ['senior', 'старший', 'опытный', 'senior-level', 'advanced'],
            'expert': ['expert', 'эксперт', 'профессионал', 'профессионал', 'advanced', 'senior']
        }
        
        # Проверяем, есть ли ключевые слова для данного уровня в описании
        if experience_level.lower() in level_keywords:
            for keyword in level_keywords[experience_level.lower()]:
                if keyword in description:
                    return True
        
        # Если в проекте есть конкретное указание уровня опыта, проверяем его
        project_experience = project_data.get('experience_level', '').lower()
        if project_experience and experience_level.lower() in project_experience:
            return True
        
        # Если в проекте нет информации об уровне опыта, считаем, что он подходит
        return True
    
    def matches_payment_type(self, project_data: Dict[str, Any], payment_type: Optional[str] = None) -> bool:
        """
        Проверяет, соответствует ли проект форме оплаты
        
        Args:
            project_data: Данные проекта
            payment_type: Форма оплаты ('fixed', 'hourly', 'per-project', 'negotiable')
            
        Returns:
            bool: Соответствует ли проект форме оплаты
        """
        if not payment_type:
            return True
            
        # Ищем информацию о форме оплаты в описании проекта
        description = project_data.get('description', '').lower()
        
        # Определяем ключевые слова для каждой формы оплаты
        payment_keywords = {
            'fixed': ['фиксирован', 'фикс. цена', 'fixed price', 'fixed budget'],
            'hourly': ['почасов', 'hourly', 'в час', 'за час'],
            'per-project': ['за проект', 'per project', 'project basis'],
            'negotiable': ['обсуждаем', 'negotiable', 'по договоренности', 'flexible']
        }
        
        # Проверяем, есть ли ключевые слова для данной формы оплаты в описании
        if payment_type.lower() in payment_keywords:
            for keyword in payment_keywords[payment_type.lower()]:
                if keyword in description:
                    return True
        
        # Если в проекте есть конкретное указание формы оплаты, проверяем его
        project_payment = project_data.get('payment_type', '').lower()
        if project_payment and payment_type.lower() in project_payment:
            return True
        
        # Если в проекте нет информации о форме оплаты, считаем, что он подходит
        return True
    
    def matches_complex_keywords(self, project_data: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Проверяет, соответствует ли проект сложным ключевым словам с поддержкой логических операторов
        
        Args:
            project_data: Данные проекта
            keywords: Список ключевых слов с поддержкой логических операторов
                     (например: ['python & django', 'javascript | react', '!php'])
            
        Returns:
            bool: Соответствует ли проект сложным ключевым словам
        """
        if not keywords:
            return True
            
        title = project_data.get('title', '').lower()
        description = project_data.get('description', '').lower()
        text_to_search = f"{title} {description}"
        
        # Проверяем каждый сложный критерий
        for keyword in keywords:
            keyword = keyword.strip()
            
            # Обрабатываем отрицательные условия (с префиксом !)
            if keyword.startswith('!'):
                exclude_keyword = keyword[1:].strip()
                if exclude_keyword.lower() in text_to_search:
                    return False  # Если найдено исключение, проект не подходит
                continue
            
            # Обрабатываем условия И (с разделителем &)
            if '&' in keyword:
                sub_keywords = [sub.strip() for sub in keyword.split('&')]
                for sub_keyword in sub_keywords:
                    if sub_keyword.lower() not in text_to_search:
                        return False  # Если не найдено хотя бы одно из условий И, проект не подходит
                continue
            
            # Обрабатываем условия ИЛИ (с разделителем |)
            if '|' in keyword:
                sub_keywords = [sub.strip() for sub in keyword.split('|')]
                found_any = False
                for sub_keyword in sub_keywords:
                    if sub_keyword.lower() in text_to_search:
                        found_any = True
                        break
                if not found_any:
                    return False  # Если не найдено ни одно из условий ИЛИ, проект не подходит
                continue
            
            # Обычное условие (если не указаны логические операторы)
            if keyword.lower() not in text_to_search:
                return False  # Если не найдено обычное условие, проект не подходит
        
        return True  # Все условия выполнены
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Внутренний метод для парсинга даты из строки
        
        Args:
            date_str: Строка с датой
            
        Returns:
            Optional[datetime]: Распознанная дата или None
        """
        # Убираем лишние пробелы
        date_str = date_str.strip()
        
        # Определяем возможные форматы даты
        date_formats = [
            "%Y-%m-%d",
            "%d.%m.%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d.%m.%Y %H:%M:%S",
            "%B %d, %Y",  # "October 15, 2023"
            "%b %d, %Y",   # "Oct 15, 2023"
            "%d %B %Y",    # "15 October 2023"
            "%d %b %Y",    # "15 Oct 2023"
        ]
        
        # Пытаемся распознать дату с помощью регулярных выражений для относительных дат
        relative_patterns = [
            (r'(\d+)\s*(день|дня|дней|day|days)\s*(спустя|через|after)', 1),
            (r'(\d+)\s*(неделя|недели|недель|week|weeks)\s*(спустя|через|after)', 7),
            (r'(\d+)\s*(месяц|месяца|месяцев|month|months)\s*(спустя|через|after)', 30),
        ]
        
        for pattern, multiplier in relative_patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                days = value * multiplier
                return datetime.now() + timedelta(days=days)
        
        # Пробуем распознать с помощью форматов
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Если не удалось распознать, возвращаем None
        return None