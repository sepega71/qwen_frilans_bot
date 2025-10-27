#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль отслеживания взаимодействия с пользователем.
Анализирует поведение пользователей для улучшения персонализации уведомлений.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class InteractionRecord:
    """Класс для хранения записи взаимодействия"""
    user_id: int
    project_id: int
    interaction_type: str  # 'view', 'click', 'ignore', 'like', 'dislike'
    timestamp: str
    source: str = "notification"


class UserInteractionTracker:
    """
    Класс для отслеживания взаимодействия пользователей с уведомлениями и проектами.
    """
    
    def __init__(self, storage_file: str = "user_interactions.json"):
        """
        Инициализация трекера взаимодействий
        
        Args:
            storage_file: Имя файла для хранения взаимодействий
        """
        self.storage_file = storage_file
        self.interactions: List[InteractionRecord] = []
        self.load_interactions()
    
    def load_interactions(self):
        """Загрузка взаимодействий из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for interaction_data in data:
                    interaction = InteractionRecord(
                        user_id=interaction_data['user_id'],
                        project_id=interaction_data['project_id'],
                        interaction_type=interaction_data['interaction_type'],
                        timestamp=interaction_data['timestamp'],
                        source=interaction_data.get('source', 'notification')
                    )
                    self.interactions.append(interaction)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Ошибка при загрузке взаимодействий: {e}")
                # Создаем пустой список, если файл поврежден
                self.interactions = []
    
    def save_interactions(self):
        """Сохранение взаимодействий в файл"""
        data = [asdict(interaction) for interaction in self.interactions]
        
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def record_interaction(self, user_id: int, project_id: int, interaction_type: str, source: str = "notification"):
        """
        Запись взаимодействия пользователя с проектом
        
        Args:
            user_id: ID пользователя
            project_id: ID проекта
            interaction_type: Тип взаимодействия ('view', 'click', 'ignore', 'like', 'dislike')
            source: Источник взаимодействия ('notification', 'search', etc.)
        """
        interaction = InteractionRecord(
            user_id=user_id,
            project_id=project_id,
            interaction_type=interaction_type,
            timestamp=datetime.now().isoformat(),
            source=source
        )
        
        self.interactions.append(interaction)
        self.save_interactions()
    
    def get_user_interactions(self, user_id: int, days: int = 30) -> List[InteractionRecord]:
        """
        Получение взаимодействий пользователя за последние N дней
        
        Args:
            user_id: ID пользователя
            days: Количество дней для поиска (по умолчанию 30)
            
        Returns:
            List[InteractionRecord]: Список взаимодействий пользователя
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        user_interactions = [
            interaction for interaction in self.interactions
            if interaction.user_id == user_id and 
            datetime.fromisoformat(interaction.timestamp) > cutoff_date
        ]
        return user_interactions
    
    def get_project_interactions(self, project_id: int) -> List[InteractionRecord]:
        """
        Получение всех взаимодействий с определенным проектом
        
        Args:
            project_id: ID проекта
            
        Returns:
            List[InteractionRecord]: Список взаимодействий с проектом
        """
        project_interactions = [
            interaction for interaction in self.interactions
            if interaction.project_id == project_id
        ]
        return project_interactions
    
    def calculate_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Расчет предпочтений пользователя на основе взаимодействий
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Словарь с предпочтениями пользователя
        """
        interactions = self.get_user_interactions(user_id)
        
        if not interactions:
            return {}
        
        # Подсчет взаимодействий по типам
        interaction_counts = defaultdict(int)
        project_interactions = defaultdict(list)
        
        for interaction in interactions:
            interaction_counts[interaction.interaction_type] += 1
            project_interactions[interaction.project_id].append(interaction.interaction_type)
        
        # Определение метрик
        total_interactions = len(interactions)
        views = interaction_counts.get('view', 0)
        clicks = interaction_counts.get('click', 0)
        likes = interaction_counts.get('like', 0)
        ignores = interaction_counts.get('ignore', 0)
        
        # Вычисление коэффициентов
        engagement_rate = (clicks + likes) / total_interactions if total_interactions > 0 else 0
        click_through_rate = clicks / views if views > 0 else 0
        
        # Определение предпочитаемых проектов (те, с которыми было больше всего позитивных взаимодействий)
        preferred_projects = []
        for project_id, interactions_list in project_interactions.items():
            positive_interactions = sum(1 for i in interactions_list if i in ['click', 'like'])
            if positive_interactions > 0:
                preferred_projects.append({
                    'project_id': project_id,
                    'positive_interactions': positive_interactions
                })
        
        # Сортировка по количеству позитивных взаимодействий
        preferred_projects.sort(key=lambda x: x['positive_interactions'], reverse=True)
        
        return {
            'engagement_rate': engagement_rate,
            'click_through_rate': click_through_rate,
            'total_interactions': total_interactions,
            'views': views,
            'clicks': clicks,
            'likes': likes,
            'ignores': ignores,
            'preferred_projects': preferred_projects[:10]  # Топ-10 проектов
        }
    
    def get_relevant_projects_by_user_history(self, user_id: int, all_projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Получение релевантных проектов для пользователя на основе истории взаимодействий
        
        Args:
            user_id: ID пользователя
            all_projects: Список всех проектов
            
        Returns:
            List[Dict[str, Any]]: Список релевантных проектов
        """
        user_preferences = self.calculate_user_preferences(user_id)
        
        if not user_preferences or not user_preferences.get('preferred_projects'):
            # Если нет истории, возвращаем все проекты
            return all_projects
        
        # Получаем ID проектов, с которыми пользователь взаимодействовал позитивно
        preferred_project_ids = {p['project_id'] for p in user_preferences['preferred_projects']}
        
        # Фильтруем проекты, исключая те, с которыми пользователь уже взаимодействовал негативно
        ignored_projects = set()
        user_interactions = self.get_user_interactions(user_id)
        for interaction in user_interactions:
            if interaction.interaction_type in ['ignore', 'dislike']:
                ignored_projects.add(interaction.project_id)
        
        # Возвращаем проекты, которые пользователь не игнорировал
        relevant_projects = [
            project for project in all_projects
            if project.get('id') not in ignored_projects
        ]
        
        # Сортируем, чтобы проекты, с которыми пользователь взаимодействовал позитивно, были в начале
        sorted_projects = []
        
        # Сначала добавляем предпочтительные проекты
        for pref_proj_id in preferred_project_ids:
            for project in relevant_projects:
                if project.get('id') == pref_proj_id:
                    sorted_projects.append(project)
                    break
        
        # Затем добавляем остальные проекты
        for project in relevant_projects:
            if project.get('id') not in preferred_project_ids:
                sorted_projects.append(project)
        
        return sorted_projects