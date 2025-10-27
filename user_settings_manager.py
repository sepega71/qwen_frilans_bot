#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для управления пользовательскими настройками.
Хранит и обрабатывает настройки фильтрации для каждого пользователя.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class UserFilters:
    """Класс для хранения фильтров пользователя"""
    keywords: List[str] = None
    technologies: List[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    regions: List[str] = None
    project_types: List[str] = None  # 'order' или 'vacancy'
    experience_level: Optional[str] = None
    payment_type: Optional[str] = None
    max_deadline_days: Optional[int] = None # Максимальное количество дней до дедлайна

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.technologies is None:
            self.technologies = []
        if self.regions is None:
            self.regions = []
        if self.project_types is None:
            self.project_types = []


@dataclass
class UserSettings:
    """Класс для хранения настроек пользователя"""
    user_id: int
    subscribed: bool = False
    filters: UserFilters = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = UserFilters()
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class UserSettingsManager:
    """
    Класс для управления пользовательскими настройками.
    Обеспечивает хранение, загрузку и сохранение настроек пользователей.
    """
    
    def __init__(self, storage_file: str = "user_settings.json"):
        """
        Инициализация менеджера настроек
        
        Args:
            storage_file: Имя файла для хранения настроек
        """
        self.storage_file = storage_file
        self.settings: Dict[int, UserSettings] = {}
        self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for user_id_str, user_data in data.items():
                    user_id = int(user_id_str)
                    
                    # Восстановление фильтров
                    filters_data = user_data.get('filters', {})
                    filters = UserFilters(
                        keywords=filters_data.get('keywords', []),
                        technologies=filters_data.get('technologies', []),
                        budget_min=filters_data.get('budget_min'),
                        budget_max=filters_data.get('budget_max'),
                        regions=filters_data.get('regions', []),
                        project_types=filters_data.get('project_types', []),
                        experience_level=filters_data.get('experience_level'),
                        payment_type=filters_data.get('payment_type'),
                        max_deadline_days=filters_data.get('max_deadline_days')
                    )
                    
                    # Восстановление настроек пользователя
                    settings = UserSettings(
                        user_id=user_id,
                        subscribed=user_data.get('subscribed', False),
                        filters=filters,
                        created_at=user_data.get('created_at'),
                        updated_at=user_data.get('updated_at')
                    )
                    
                    self.settings[user_id] = settings
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Ошибка при загрузке настроек: {e}")
                # Создаем пустой словарь, если файл поврежден
                self.settings = {}
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        data = {}
        for user_id, settings in self.settings.items():
            data[user_id] = {
                'user_id': settings.user_id,
                'subscribed': settings.subscribed,
                'filters': asdict(settings.filters),
                'created_at': settings.created_at,
                'updated_at': settings.updated_at
            }
        
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_user_settings(self, user_id: int) -> UserSettings:
        """
        Получение настроек пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserSettings: Настройки пользователя
        """
        if user_id not in self.settings:
            # Создание новых настроек для пользователя
            self.settings[user_id] = UserSettings(user_id=user_id)
            self.save_settings()
        
        return self.settings[user_id]
    
    def update_user_subscription(self, user_id: int, subscribed: bool):
        """
        Обновление статуса подписки пользователя
        
        Args:
            user_id: ID пользователя
            subscribed: Статус подписки
        """
        settings = self.get_user_settings(user_id)
        settings.subscribed = subscribed
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def add_keywords(self, user_id: int, keywords: List[str]):
        """
        Добавление ключевых слов в фильтр пользователя
        
        Args:
            user_id: ID пользователя
            keywords: Список ключевых слов
        """
        settings = self.get_user_settings(user_id)
        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword not in settings.filters.keywords:
                settings.filters.keywords.append(keyword)
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def remove_keywords(self, user_id: int, keywords: List[str]):
        """
        Удаление ключевых слов из фильтра пользователя
        
        Args:
            user_id: ID пользователя
            keywords: Список ключевых слов для удаления
        """
        settings = self.get_user_settings(user_id)
        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword in settings.filters.keywords:
                settings.filters.keywords.remove(keyword)
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def add_technologies(self, user_id: int, technologies: List[str]):
        """
        Добавление технологий в фильтр пользователя
        
        Args:
            user_id: ID пользователя
            technologies: Список технологий
        """
        settings = self.get_user_settings(user_id)
        for technology in technologies:
            technology = technology.strip().lower()
            if technology not in settings.filters.technologies:
                settings.filters.technologies.append(technology)
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def remove_technologies(self, user_id: int, technologies: List[str]):
        """
        Удаление технологий из фильтра пользователя
        
        Args:
            user_id: ID пользователя
            technologies: Список технологий для удаления
        """
        settings = self.get_user_settings(user_id)
        for technology in technologies:
            technology = technology.strip().lower()
            if technology in settings.filters.technologies:
                settings.filters.technologies.remove(technology)
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def set_budget(self, user_id: int, min_budget: Optional[int] = None, max_budget: Optional[int] = None):
        """
        Установка диапазона бюджета для пользователя
        
        Args:
            user_id: ID пользователя
            min_budget: Минимальный бюджет
            max_budget: Максимальный бюджет
        """
        settings = self.get_user_settings(user_id)
        
        if min_budget is not None:
            settings.filters.budget_min = min_budget
        if max_budget is not None:
            settings.filters.budget_max = max_budget
            
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def set_regions(self, user_id: int, regions: List[str]):
        """
        Установка регионов для пользователя
        
        Args:
            user_id: ID пользователя
            regions: Список регионов
        """
        settings = self.get_user_settings(user_id)
        for region in regions:
            region = region.strip().lower()
            if region not in settings.filters.regions:
                settings.filters.regions.append(region)
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def set_project_types(self, user_id: int, project_types: List[str]):
        """
        Установка типов проектов для пользователя
        
        Args:
            user_id: ID пользователя
            project_types: Список типов проектов ('order', 'vacancy')
        """
        settings = self.get_user_settings(user_id)
        valid_types = {'order', 'vacancy'}
        
        for project_type in project_types:
            project_type = project_type.strip().lower()
            if project_type in valid_types and project_type not in settings.filters.project_types:
                settings.filters.project_types.append(project_type)
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def set_experience_level(self, user_id: int, level: str):
        """
        Установка уровня опыта для пользователя
        
        Args:
            user_id: ID пользователя
            level: Уровень опыта
        """
        settings = self.get_user_settings(user_id)
        settings.filters.experience_level = level.lower()
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def set_payment_type(self, user_id: int, payment_type: str):
        """
        Установка формы оплаты для пользователя
        
        Args:
            user_id: ID пользователя
            payment_type: Форма оплаты
        """
        settings = self.get_user_settings(user_id)
        settings.filters.payment_type = payment_type.lower()
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def set_deadline(self, user_id: int, max_deadline_days: Optional[int] = None):
        """
        Установка максимального срока выполнения проекта для пользователя
        
        Args:
            user_id: ID пользователя
            max_deadline_days: Максимальное количество дней до дедлайна
        """
        settings = self.get_user_settings(user_id)
        settings.filters.max_deadline_days = max_deadline_days
        settings.updated_at = datetime.now().isoformat()
        self.save_settings()
    
    def get_subscribed_users(self) -> List[UserSettings]:
        """
        Получение списка всех подписанных пользователей
        
        Returns:
            List[UserSettings]: Список настроек подписанных пользователей
        """
        return [settings for settings in self.settings.values() if settings.subscribed]
    
    def get_matching_users(self, project_data: Dict[str, Any]) -> List[UserSettings]:
        """
        Поиск пользователей, подходящих под проект
        
        Args:
            project_data: Данные проекта для проверки
            
        Returns:
            List[UserSettings]: Список настроек пользователей, подходящих под проект
        """
        matching_users = []
        
        for settings in self.settings.values():
            if not settings.subscribed:
                continue
                
            if self._matches_filters(settings.filters, project_data):
                matching_users.append(settings)
        
        return matching_users
    
    def _matches_filters(self, filters: UserFilters, project_data: Dict[str, Any]) -> bool:
        """
        Проверка соответствия проекта фильтрам пользователя
        
        Args:
            filters: Фильтры пользователя
            project_data: Данные проекта
            
        Returns:
            bool: Соответствует ли проект фильтрам
        """
        # Проверка ключевых слов
        if filters.keywords:
            title = project_data.get('title', '').lower()
            description = project_data.get('description', '').lower()
            text_to_search = f"{title} {description}"
            
            keyword_match = any(keyword in text_to_search for keyword in filters.keywords)
            if not keyword_match:
                return False
        
        # Проверка технологий
        if filters.technologies:
            technologies = project_data.get('technologies', [])
            if technologies:
                # Приведение к нижнему регистру для сравнения
                tech_list = [tech.lower() for tech in technologies]
                tech_match = any(tech in tech_list for tech in filters.technologies)
                if not tech_match:
                    return False
            else:
                # Если в проекте нет технологий, но пользователь фильтрует по ним, пропускаем
                return False
        
        # Проверка бюджета
        budget = project_data.get('budget')
        if budget is not None and (filters.budget_min is not None or filters.budget_max is not None):
            if filters.budget_min is not None and budget < filters.budget_min:
                return False
            if filters.budget_max is not None and budget > filters.budget_max:
                return False
        
        # Проверка регионов
        if filters.regions:
            region = project_data.get('region', '').lower()
            if region and filters.regions:
                region_match = any(user_region in region for user_region in filters.regions)
                if not region_match:
                    return False
        
        # Проверка типов проектов
        if filters.project_types:
            project_type = project_data.get('type', '').lower()
            if project_type and filters.project_types:
                if project_type not in filters.project_types:
                    return False
        
        # Проверка уровня опыта (пока без проверки, так как в проекте может не быть этой информации)
        if filters.experience_level:
            # В реальной реализации нужно проверить, соответствует ли проект уровню опыта
            # Пока возвращаем True, так как в большинстве источников нет информации об уровне опыта
            pass
        
        # Проверка формы оплаты (пока без проверки, так как в проекте может не быть этой информации)
        if filters.payment_type:
            # В реальной реализации нужно проверить, соответствует ли проект форме оплаты
            # Пока возвращаем True, так как в большинстве источников нет информации о форме оплаты
            pass
        
        # Проверка сроков выполнения
        if filters.max_deadline_days is not None:
            # В реальной реализации нужно проверить, соответствует ли проект срокам выполнения
            # Пока возвращаем True, так как в большинстве источников нет информации о дедлайне
            pass
        
        return True