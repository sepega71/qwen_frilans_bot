#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль управления.
Мониторит состояние системы, обеспечивает логирование и аудит.
Управляет конфигурацией системы.
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditEventType(Enum):
    """Типы событий аудита"""
    USER_REGISTERED = "USER_REGISTERED"
    USER_SETTINGS_UPDATED = "USER_SETTINGS_UPDATED"
    PROJECT_FETCHED = "PROJECT_FETCHED"
    NOTIFICATION_SENT = "NOTIFICATION_SENT"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CONFIG_CHANGED = "CONFIG_CHANGED"


@dataclass
class SystemConfig:
    """Конфигурация системы"""
    check_interval_minutes: int = 60
    max_projects_per_notification: int = 5
    log_level: str = "INFO"
    enable_auditing: bool = True
    max_log_size_mb: int = 10
    max_log_files: int = 5
    data_retention_days: int = 30


class ManagementModule:
    """
    Класс для управления системой.
    """
    
    def __init__(self, config_file: str = "system_config.json"):
        """
        Инициализация модуля управления
        
        Args:
            config_file: Путь к файлу конфигурации
        """
        self.config_file = config_file
        self.config = self.load_config()
        self.logger = self.setup_logging()
        self.audit_logger = self.setup_audit_logging()
    
    def load_config(self) -> SystemConfig:
        """
        Загрузка конфигурации системы
        
        Returns:
            SystemConfig: Конфигурация системы
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Создаем конфигурацию с возможностью обновления из файла
            config = SystemConfig()
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            return config
        except FileNotFoundError:
            # Если файл конфигурации не найден, используем значения по умолчанию
            return SystemConfig()
        except Exception as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            return SystemConfig()
    
    def save_config(self):
        """Сохранение конфигурации системы"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.config), f, ensure_ascii=False, indent=2)
    
    def setup_logging(self) -> logging.Logger:
        """
        Настройка основного логирования
        
        Returns:
            logging.Logger: Логгер системы
        """
        logger = logging.getLogger('frilans_bot')
        logger.setLevel(getattr(logging, self.config.log_level))
        
        # Удаляем существующие обработчики
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def setup_audit_logging(self) -> logging.Logger:
        """
        Настройка логирования аудита
        
        Returns:
            logging.Logger: Логгер аудита
        """
        logger = logging.getLogger('frilans_bot_audit')
        logger.setLevel(logging.INFO)
        
        # Удаляем существующие обработчики
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Создаем форматтер для аудита
        formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        
        # Обработчик для вывода в консоль
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_event(self, level: LogLevel, message: str):
        """
        Логирование события
        
        Args:
            level: Уровень логирования
            message: Сообщение
        """
        getattr(self.logger, level.value.lower())(message)
    
    def audit_event(self, event_type: AuditEventType, user_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        """
        Логирование события аудита
        
        Args:
            event_type: Тип события
            user_id: ID пользователя (если применимо)
            details: Дополнительные детали события
        """
        if not self.config.enable_auditing:
            return
        
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'user_id': user_id,
            'details': details or {}
        }
        
        self.audit_logger.info(json.dumps(event_data, ensure_ascii=False))
    
    def update_config(self, **kwargs):
        """
        Обновление конфигурации системы
        
        Args:
            **kwargs: Параметры конфигурации для обновления
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.log_event(LogLevel.INFO, f"Конфигурация обновлена: {key} = {value}")
        
        self.save_config()
        self.audit_event(AuditEventType.CONFIG_CHANGED, details=kwargs)
        
        # Перенастраиваем логирование при изменении уровня
        if 'log_level' in kwargs:
            self.logger = self.setup_logging()
    
    async def monitor_system_status(self) -> Dict[str, Any]:
        """
        Мониторинг состояния системы
        
        Returns:
            Dict[str, Any]: Состояние системы
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'config': asdict(self.config),
            'active_tasks': [],
            'system_health': 'OK',
            'last_data_collection': None,
            'last_notification_sent': None
        }
        
        # Здесь можно добавить проверки работоспособности различных компонентов
        # например, проверка подключения к базе данных, внешним API и т.д.
        
        return status
    
    async def cleanup_old_data(self):
        """Очистка старых данных в соответствии с политикой хранения"""
        # В реальной системе здесь будет реализация очистки старых записей
        # из базы данных в соответствии с config.data_retention_days
        self.log_event(LogLevel.INFO, f"Очистка данных старше {self.config.data_retention_days} дней")
    
    async def run_maintenance_tasks(self):
        """Выполнение задач технического обслуживания"""
        while True:
            try:
                self.log_event(LogLevel.INFO, "Запуск задач технического обслуживания")
                
                # Очистка старых данных
                await self.cleanup_old_data()
                
                # Мониторинг состояния системы
                status = await self.monitor_system_status()
                self.log_event(LogLevel.INFO, f"Состояние системы: {status['system_health']}")
                
                # Задержка перед следующим выполнением задач
                await asyncio.sleep(self.config.check_interval_minutes * 60)
            except Exception as e:
                self.log_event(LogLevel.ERROR, f"Ошибка в задачах технического обслуживания: {e}")
                # Делаем паузу перед следующей попыткой
                await asyncio.sleep(60)