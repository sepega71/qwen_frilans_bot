#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль фильтрации заказов и вакансий.
Применяет пользовательские фильтры к собранным данным.
"""

from typing import Dict, List, Any, Optional
from user_settings_manager import UserSettings, UserFilters
from .advanced_filter import AdvancedFilterEngine


class FilterEngine:
    """
    Класс для фильтрации заказов и вакансий по пользовательским критериям.
    """
    
    def __init__(self):
        """Инициализация движка фильтрации"""
        self.advanced_filter = AdvancedFilterEngine()
    
    def matches_keywords(self, project_data: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Проверяет, соответствует ли проект ключевым словам
        
        Args:
            project_data: Данные проекта
            keywords: Список ключевых слов
            
        Returns:
            bool: Соответствует ли проект ключевым словам
        """
        if not keywords:
            return True
            
        title = project_data.get('title', '').lower()
        description = project_data.get('description', '').lower()
        text_to_search = f"{title} {description}"
        
        return any(keyword.lower() in text_to_search for keyword in keywords)
    
    def matches_technologies(self, project_data: Dict[str, Any], technologies: List[str]) -> bool:
        """
        Проверяет, соответствует ли проект технологиям
        
        Args:
            project_data: Данные проекта
            technologies: Список технологий
            
        Returns:
            bool: Соответствует ли проект технологиям
        """
        if not technologies:
            return True
            
        project_technologies = project_data.get('technologies', [])
        if not project_technologies:
            # Если в проекте нет технологий, но пользователь фильтрует по ним, 
            # считаем, что проект не подходит
            return False
            
        # Приведение к нижнему регистру для сравнения
        project_tech_lower = [tech.lower() for tech in project_technologies]
        return any(tech.lower() in project_tech_lower for tech in technologies)
    
    def matches_budget(self, project_data: Dict[str, Any], min_budget: int = None, max_budget: int = None) -> bool:
        """
        Проверяет, соответствует ли проект бюджету
        
        Args:
            project_data: Данные проекта
            min_budget: Минимальный бюджет
            max_budget: Максимальный бюджет
            
        Returns:
            bool: Соответствует ли проект бюджету
        """
        if min_budget is None and max_budget is None:
            return True
            
        budget = project_data.get('budget')
        if budget is None:
            # Если бюджет не указан в проекте, считаем, что он подходит
            return True
            
        if min_budget is not None and budget < min_budget:
            return False
            
        if max_budget is not None and budget > max_budget:
            return False
            
        return True
    
    def matches_region(self, project_data: Dict[str, Any], regions: List[str]) -> bool:
        """
        Проверяет, соответствует ли проект региону
        
        Args:
            project_data: Данные проекта
            regions: Список регионов
            
        Returns:
            bool: Соответствует ли проект региону
        """
        if not regions:
            return True
            
        region = project_data.get('region', '').lower()
        if not region:
            # Если регион не указан, считаем, что он подходит
            return True
            
        return any(user_region.lower() in region for user_region in regions)
    
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
            
        # Временная заглушка - в реальной реализации нужно извлекать дату дедлайна из проекта
        # и сравнивать с текущей датой + max_deadline_days
        # deadline_str = project_data.get('deadline')
        # if deadline_str:
        #     try:
        #         deadline = datetime.fromisoformat(deadline_str)
        #         current_time = datetime.now()
        #         delta = (deadline - current_time).days
        #         return delta <= max_deadline_days
        #     except ValueError:
        #         pass  # Если формат даты неправильный, пропускаем проверку
        
        # Пока возвращаем True, так как в большинстве источников нет информации о дедлайне
        return True
    
    def matches_project_type(self, project_data: Dict[str, Any], project_types: List[str]) -> bool:
        """
        Проверяет, соответствует ли проект типу
        
        Args:
            project_data: Данные проекта
            project_types: Список типов проектов
            
        Returns:
            bool: Соответствует ли проект типу
        """
        if not project_types:
            return True
            
        project_type = project_data.get('type', '').lower()
        if not project_type:
            # Если тип не указан, считаем, что он подходит
            return True
            
        return project_type in project_types
    
    def matches_filters(self, project_data: Dict[str, Any], user_filters: UserFilters) -> bool:
        """
        Проверяет, соответствует ли проект всем фильтрам пользователя
        
        Args:
            project_data: Данные проекта
            user_filters: Фильтры пользователя
            
        Returns:
            bool: Соответствует ли проект фильтрам
        """
        # Проверка ключевых слов
        if not self.matches_keywords(project_data, user_filters.keywords):
            return False

        # Проверка технологий
        if not self.matches_technologies(project_data, user_filters.technologies):
            return False

        # Проверка бюджета
        if not self.matches_budget(
            project_data,
            user_filters.budget_min,
            user_filters.budget_max
        ):
            return False

        # Проверка регионов
        if not self.matches_region(project_data, user_filters.regions):
            return False

        # Проверка типов проектов
        if not self.matches_project_type(project_data, user_filters.project_types):
            return False

        # Проверка сроков выполнения
        if not self.matches_deadline(project_data, user_filters.max_deadline_days):
            return False

        # Проверка уровня опыта
        if not self.advanced_filter.matches_experience_level(project_data, user_filters.experience_level):
            return False

        # Проверка формы оплаты
        if not self.advanced_filter.matches_payment_type(project_data, user_filters.payment_type):
            return False

        # Проверка сложных ключевых слов
        if not self.advanced_filter.matches_complex_keywords(project_data, user_filters.keywords):
            return False

        return True
    
    def filter_projects(self, projects: List[Dict[str, Any]], user_filters: UserFilters) -> List[Dict[str, Any]]:
        """
        Фильтрация списка проектов по пользовательским фильтрам
        
        Args:
            projects: Список проектов
            user_filters: Фильтры пользователя
            
        Returns:
            List[Dict[str, Any]]: Отфильтрованный список проектов
        """
        filtered_projects = []
        
        for project in projects:
            if self.matches_filters(project, user_filters):
                filtered_projects.append(project)
        
        return filtered_projects