#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль персонализации уведомлений.
Управляет профилями пользователей и их предпочтениями.
Определяет релевантные заказы и вакансии для каждого пользователя.
"""

from typing import Dict, List, Any
from user_settings_manager import UserSettingsManager, UserSettings
from filter_engine import FilterEngine


class PersonalizationEngine:
    """
    Класс для персонализации уведомлений для пользователей.
    """
    
    def __init__(self, user_settings_manager: UserSettingsManager, filter_engine: FilterEngine):
        """
        Инициализация движка персонализации
        
        Args:
            user_settings_manager: Менеджер пользовательских настроек
            filter_engine: Движок фильтрации
        """
        self.user_settings_manager = user_settings_manager
        self.filter_engine = filter_engine
    
    def get_relevant_projects_for_user(self, user_settings: UserSettings, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Получение релевантных проектов для пользователя
        
        Args:
            user_settings: Настройки пользователя
            projects: Список проектов
            
        Returns:
            List[Dict[str, Any]]: Список релевантных проектов
        """
        if not user_settings.subscribed:
            return []
        
        return self.filter_engine.filter_projects(projects, user_settings.filters)
    
    def get_relevant_projects_for_all_users(self, projects: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Получение релевантных проектов для всех пользователей
        
        Args:
            projects: Список проектов
            
        Returns:
            Dict[int, List[Dict[str, Any]]]: Словарь с ID пользователя и списком релевантных проектов
        """
        relevant_projects = {}
        
        # Получаем всех подписанных пользователей
        subscribed_users = self.user_settings_manager.get_subscribed_users()
        
        for user_settings in subscribed_users:
            user_projects = self.get_relevant_projects_for_user(user_settings, projects)
            if user_projects:
                relevant_projects[user_settings.user_id] = user_projects
        
        return relevant_projects
    
    def format_project_message(self, project: Dict[str, Any]) -> str:
        """
        Форматирование сообщения о проекте для отправки пользователю
        
        Args:
            project: Данные проекта
            
        Returns:
            str: Отформатированное сообщение
        """
        title = project.get('title', 'Без названия')
        description = project.get('description', 'Без описания')
        budget = project.get('budget')
        region = project.get('region', 'Не указан')
        project_type = project.get('type', 'Проект')
        technologies = project.get('technologies', [])
        url = project.get('url', '')
        
        # Определение типа проекта для отображения
        type_label = 'Заказ' if project_type.lower() == 'order' else 'Вакансия' if project_type.lower() == 'vacancy' else 'Проект'
        
        message = f"🆕 {type_label}\n\n"
        message += f"📝 <b>{title}</b>\n\n"
        
        if description:
            # Ограничиваем длину описания
            if len(description) > 300:
                description = description[:297] + "..."
            message += f"📋 <i>{description}</i>\n\n"
        
        if budget is not None:
            message += f"💰 Бюджет: {budget} руб.\n"
        
        if region:
            message += f"🌍 Регион: {region}\n"
        
        if technologies:
            message += f"🛠️ Технологии: {', '.join(technologies)}\n"
        
        if url:
            message += f"\n🔗 Ссылка: {url}"
        
        return message
    
    def get_personalized_notifications(self, projects: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """
        Получение персонализированных уведомлений для всех пользователей
        
        Args:
            projects: Список проектов
            
        Returns:
            Dict[int, List[str]]: Словарь с ID пользователя и списком сообщений для уведомлений
        """
        notifications = {}
        
        # Получаем релевантные проекты для всех пользователей
        relevant_projects = self.get_relevant_projects_for_all_users(projects)
        
        # Форматируем сообщения для каждого пользователя
        for user_id, user_projects in relevant_projects.items():
            user_notifications = []
            for project in user_projects:
                message = self.format_project_message(project)
                user_notifications.append(message)
            
            if user_notifications:
                notifications[user_id] = user_notifications
        
        return notifications