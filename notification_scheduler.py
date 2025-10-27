#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль планировщика уведомлений.
Управляет расписанием отправки персонализированных уведомлений пользователям.
"""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Any
from notification_engine import NotificationEngine
from data_storage import DataStorage
from personalization_engine import PersonalizationEngine


class NotificationScheduler:
    """
    Класс для планирования уведомлений.
    """
    
    def __init__(self, notification_engine: NotificationEngine, data_storage: DataStorage, 
                 personalization_engine: PersonalizationEngine):
        """
        Инициализация планировщика уведомлений
        
        Args:
            notification_engine: Движок уведомлений
            data_storage: Хранилище данных
            personalization_engine: Движок персонализации
        """
        self.notification_engine = notification_engine
        self.data_storage = data_storage
        self.personalization_engine = personalization_engine
        self.logger = logging.getLogger(__name__)
        self.daily_notification_time = time(10, 0)  # Время ежедневной рассылки (10:00 по умолчанию)
        self.is_running = False
    
    def set_daily_notification_time(self, hour: int, minute: int):
        """
        Установка времени для ежедневной рассылки
        
        Args:
            hour: Час (0-23)
            minute: Минута (0-59)
        """
        self.daily_notification_time = time(hour, minute)
        self.logger.info(f"Время ежедневной рассылки установлено на {self.daily_notification_time}")
    
    async def send_daily_digest(self) -> Dict[int, int]:
        """
        Отправка ежедневного дайджеста пользователям
        
        Returns:
            Dict[int, int]: Словарь с ID пользователя и количеством отправленных уведомлений
        """
        # Получаем последние проекты за последние 24 часа
        recent_projects = self.data_storage.get_recent_projects(limit=50)
        
        # Формируем персонализированные уведомления
        notifications = self.personalization_engine.get_personalized_notifications(recent_projects)
        
        # Добавляем заголовок дайджеста к каждому сообщению
        for user_id, messages in notifications.items():
            if messages:
                # Добавляем заголовок в начало
                digest_header = f"📰 Ежедневный дайджест: {len(messages)} новых предложений для вас!"
                messages[0] = f"{digest_header}\n\n{messages[0]}"
        
        # Отправляем уведомления
        results = await self.notification_engine.send_bulk_notifications(notifications)
        return results
    
    async def schedule_daily_notifications(self):
        """
        Планирование ежедневных уведомлений
        """
        self.logger.info(f"Запуск планировщика ежедневных уведомлений. Время рассылки: {self.daily_notification_time}")
        self.is_running = True
        
        while self.is_running:
            try:
                now = datetime.now()
                # Определяем время следующей отправки
                next_send_time = datetime.combine(now.date(), self.daily_notification_time)
                
                # Если время уже прошло сегодня, планируем на следующий день
                if now.time() > self.daily_notification_time:
                    next_send_time = datetime.combine(now.date(), self.daily_notification_time) + timedelta(days=1)
                
                # Вычисляем время до следующей отправки
                time_to_wait = (next_send_time - now).total_seconds()
                
                self.logger.info(f"Следующая отправка дайджеста запланирована на {next_send_time}")
                
                # Ждем до времени отправки
                await asyncio.sleep(time_to_wait)
                
                # Отправляем дайджест
                results = await self.send_daily_digest()
                
                # Логируем результаты
                for user_id, sent_count in results.items():
                    if sent_count > 0:
                        self.logger.info(f"Дайджест: отправлено {sent_count} уведомлений пользователю {user_id}")
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле ежедневных уведомлений: {e}")
                # Делаем паузу перед следующей попыткой
                await asyncio.sleep(60)
    
    async def start_scheduler(self):
        """
        Запуск планировщика в фоновом режиме
        """
        asyncio.create_task(self.schedule_daily_notifications())
    
    def stop_scheduler(self):
        """
        Остановка планировщика
        """
        self.is_running = False