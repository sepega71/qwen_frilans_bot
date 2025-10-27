#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль уведомлений.
Отправляет персонализированные уведомления пользователям.
Управляет расписанием рассылки.
"""

import asyncio
import logging
from typing import Dict, List, Any
from telegram import Bot
from user_settings_manager import UserSettingsManager
from data_storage import DataStorage
from personalization_engine import PersonalizationEngine
from datetime import datetime, timedelta


class NotificationEngine:
    """
    Класс для управления уведомлениями.
    """
    
    def __init__(self, bot_token: str, user_settings_manager: UserSettingsManager, data_storage: DataStorage, personalization_engine: PersonalizationEngine):
        """
        Инициализация движка уведомлений
        
        Args:
            bot_token: Токен телеграм-бота
            user_settings_manager: Менеджер пользовательских настроек
            data_storage: Хранилище данных
            personalization_engine: Движок персонализации
        """
        self.bot = Bot(token=bot_token)
        self.user_settings_manager = user_settings_manager
        self.data_storage = data_storage
        self.personalization_engine = personalization_engine
        self.logger = logging.getLogger(__name__)
    
    async def send_notification(self, user_id: int, message: str) -> bool:
        """
        Отправка уведомления пользователю
        
        Args:
            user_id: ID пользователя
            message: Текст уведомления
            
        Returns:
            bool: Успешно ли отправлено уведомление
        """
        try:
            await self.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
            self.logger.info(f"Уведомление отправлено пользователю {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
            return False
    
    async def send_bulk_notifications(self, notifications: Dict[int, List[str]]) -> Dict[int, int]:
        """
        Массовая отправка уведомлений пользователям
        
        Args:
            notifications: Словарь с ID пользователя и списком сообщений для уведомлений
            
        Returns:
            Dict[int, int]: Словарь с ID пользователя и количеством отправленных уведомлений
        """
        results = {}
        
        for user_id, messages in notifications.items():
            sent_count = 0
            
            for message in messages:
                success = await self.send_notification(user_id, message)
                if success:
                    sent_count += 1
                # Небольшая задержка между отправками, чтобы не спамить
                await asyncio.sleep(0.1)
            
            results[user_id] = sent_count
        
        return results
    
    async def send_project_notifications(self, project_notifications: Dict[int, List[str]]) -> Dict[int, int]:
        """
        Отправка уведомлений о новых проектах пользователям
        
        Args:
            project_notifications: Словарь с ID пользователя и списком сообщений о проектах
            
        Returns:
            Dict[int, int]: Словарь с ID пользователя и количеством отправленных уведомлений
        """
        # Проверяем, подписан ли пользователь перед отправкой
        filtered_notifications = {}
        
        for user_id, messages in project_notifications.items():
            user_settings = self.user_settings_manager.get_user_settings(user_id)
            if user_settings.subscribed and messages:
                filtered_notifications[user_id] = messages
        
        return await self.send_bulk_notifications(filtered_notifications)
    
    async def schedule_regular_notifications(self, interval_minutes: int = 60):
        """
        Планирование регулярных уведомлений
        
        Args:
            interval_minutes: Интервал между уведомлениями в минутах
        """
        while True:
            try:
                # Здесь должна быть реализация получения новых проектов
                # и отправки уведомлений (в реальном приложении)
                self.logger.info("Проверка новых проектов для уведомлений...")
                
                # Имитация задержки
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                self.logger.error(f"Ошибка в цикле регулярных уведомлений: {e}")
                # Делаем паузу перед следующей попыткой
                await asyncio.sleep(60)
    
    async def send_notification_with_history_tracking(self, user_id: int, message: str, project_id: int = None) -> bool:
        """
        Отправка уведомления пользователю с отслеживанием истории
        
        Args:
            user_id: ID пользователя
            message: Текст уведомления
            project_id: ID проекта (опционально)
            
        Returns:
            bool: Успешно ли отправлено уведомление
        """
        success = await self.send_notification(user_id, message)
        if success and project_id:
            # Отмечаем проект как отправленный пользователю
            self.data_storage.mark_project_as_seen(user_id, project_id)
        return success
    
    async def send_personalized_notifications_for_projects(self, projects: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        Отправка персонализированных уведомлений о новых проектах
        
        Args:
            projects: Список проектов для отправки
             
        Returns:
            Dict[int, int]: Словарь с ID пользователя и количеством отправленных уведомлений
        """
        # Получаем персонализированные уведомления для всех пользователей
        notifications = self.personalization_engine.get_personalized_notifications(projects)
        results = {}
        
        for user_id, messages in notifications.items():
            sent_count = 0
            user_projects = self.personalization_engine.get_relevant_projects_for_user(
                self.user_settings_manager.get_user_settings(user_id), projects
            )
            
            for i, message in enumerate(messages):
                project_id = user_projects[i].get('id') if i < len(user_projects) else None
                success = await self.send_notification_with_history_tracking(user_id, message, project_id)
                if success:
                    sent_count += 1
                # Небольшая задержка между отправками, чтобы не спамить
                await asyncio.sleep(0.1)
             
            results[user_id] = sent_count
             
        return results
    
    async def schedule_intelligent_notifications(self, check_interval_minutes: int = 30, lookback_hours: int = 1):
        """
        Планирование интеллектуальных уведомлений на основе новых проектов
        
        Args:
            check_interval_minutes: Интервал проверки новых проектов в минутах
            lookback_hours: Количество часов для поиска новых проектов
        """
        self.logger.info("Запуск цикла интеллектуальных уведомлений...")
         
        while True:
            try:
                # Определяем время для поиска новых проектов
                since_time = datetime.now() - timedelta(hours=lookback_hours)
                 
                # Получаем последние проекты из хранилища
                recent_projects = self.data_storage.get_recent_projects(limit=100)
                 
                # Фильтруем проекты, которые появились с момента последней проверки
                new_projects = [
                    project for project in recent_projects
                    if datetime.fromisoformat(project['date']) > since_time
                ]
                 
                if new_projects:
                    self.logger.info(f"Найдено {len(new_projects)} новых проектов для отправки уведомлений")
                    results = await self.send_personalized_notifications_for_projects(new_projects)
                     
                    # Логируем результаты отправки
                    for user_id, sent_count in results.items():
                        if sent_count > 0:
                            self.logger.info(f"Отправлено {sent_count} уведомлений пользователю {user_id}")
                             
                else:
                    self.logger.info("Новых проектов для уведомлений не найдено")
                     
                # Имитация задержки перед следующей проверкой
                await asyncio.sleep(check_interval_minutes * 60)
                 
            except Exception as e:
                self.logger.error(f"Ошибка в цикле интеллектуальных уведомлений: {e}")
                # Делаем паузу перед следующей попыткой
                await asyncio.sleep(60)