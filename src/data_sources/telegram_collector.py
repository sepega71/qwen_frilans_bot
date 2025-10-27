#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль мониторинга Telegram-каналов
Реализует функциональность для получения сообщений из Telegram-каналов с использованием Telegram API.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import PeerChannel, Message
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import re


class TelegramCollector:
    """
    Класс для мониторинга Telegram-каналов
    Поддерживает получение сообщений из публичных и приватных каналов
    """
    
    def __init__(self, api_id: str, api_hash: str, phone: str):
        """
        Инициализация сборщика данных из Telegram
        
        Args:
            api_id: API ID приложения Telegram
            api_hash: API Hash приложения Telegram
            phone: Номер телефона для аутентификации
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Инициализация Telegram клиента"""
        try:
            self.client = TelegramClient('session_name', self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            
            if not await self.client.is_user_authorized():
                raise Exception("Пользователь не авторизован. Проверьте учетные данные.")
                
            self.logger.info("Telegram клиент успешно инициализирован")
        except SessionPasswordNeededError:
            raise Exception("Требуется ввод двухфакторной аутентификации")
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Telegram клиента: {e}")
            raise
    
    async def collect_from_channel(self, channel_username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Сбор сообщений из Telegram-канала
        
        Args:
            channel_username: Имя канала (без @)
            limit: Количество сообщений для получения
            
        Returns:
            List[Dict[str, Any]]: Список сообщений из канала
        """
        if not self.client:
            raise RuntimeError("Telegram клиент не инициализирован. Вызовите initialize() сначала.")
        
        messages = []
        
        try:
            # Получаем сущность канала
            entity = await self.client.get_entity(channel_username)
            
            # Получаем последние сообщения
            async for message in self.client.iter_messages(entity, limit=limit):
                if message:
                    processed_message = self._process_message(message, channel_username)
                    if processed_message:
                        messages.append(processed_message)
        
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait error: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            self.logger.error(f"Ошибка при сборе данных из канала {channel_username}: {e}")
        
        return messages
    
    async def collect_from_channels(self, channel_usernames: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Сбор сообщений из нескольких Telegram-каналов
        
        Args:
            channel_usernames: Список имен каналов (без @)
            limit: Количество сообщений для получения из каждого канала
            
        Returns:
            List[Dict[str, Any]]: Список сообщений из всех каналов
        """
        all_messages = []
        
        for channel_username in channel_usernames:
            try:
                channel_messages = await self.collect_from_channel(channel_username, limit)
                all_messages.extend(channel_messages)
            except Exception as e:
                self.logger.error(f"Ошибка при сборе из канала {channel_username}: {e}")
        
        return all_messages
    
    def _process_message(self, message: Message, channel_username: str) -> Optional[Dict[str, Any]]:
        """
        Обработка отдельного сообщения
        
        Args:
            message: Объект сообщения из Telegram
            channel_username: Имя канала
            
        Returns:
            Optional[Dict[str, Any]]: Обработанное сообщение или None
        """
        try:
            # Игнорируем сообщения с медиа, если только текстовые сообщения
            if message.message:
                # Извлекаем текст сообщения
                text = message.message
                
                # Извлекаем дату
                date = message.date.isoformat() if message.date else datetime.now().isoformat()
                
                # Извлекаем упоминания и хештеги
                hashtags = re.findall(r'#\w+', text)
                mentions = re.findall(r'@\w+', text)
                
                # Извлекаем URL из сообщения
                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
                
                processed = {
                    'title': f"Новое сообщение в {channel_username}",
                    'description': text,
                    'url': f"https://t.me/{channel_username}/{message.id}" if message.id else '',
                    'date': date,
                    'source': f"t.me/{channel_username}",
                    'type': 'order',  # Можно определить тип на основе контента
                    'external_id': f"telegram_{channel_username}_{message.id}",
                    'channel': channel_username,
                    'message_id': message.id,
                    'hashtags': hashtags,
                    'mentions': mentions,
                    'urls': urls,
                    'views': getattr(message, 'views', 0),
                    'forwards': getattr(message, 'forwards', 0)
                }
                
                return processed
        except Exception as e:
            self.logger.error(f"Ошибка при обработке сообщения: {e}")
        
        return None
    
    async def search_in_channel(self, channel_username: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск сообщений в Telegram-канале по запросу
        
        Args:
            channel_username: Имя канала (без @)
            query: Поисковый запрос
            limit: Количество сообщений для получения
            
        Returns:
            List[Dict[str, Any]]: Список найденных сообщений
        """
        if not self.client:
            raise RuntimeError("Telegram клиент не инициализирован. Вызовите initialize() сначала.")
        
        messages = []
        
        try:
            # Получаем сущность канала
            entity = await self.client.get_entity(channel_username)
            
            # Выполняем поиск в канале
            async for message in self.client.iter_messages(entity, limit=limit, search=query):
                if message:
                    processed_message = self._process_message(message, channel_username)
                    if processed_message:
                        messages.append(processed_message)
        
        except FloodWaitError as e:
            self.logger.warning(f"Flood wait error: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            self.logger.error(f"Ошибка при поиске в канале {channel_username}: {e}")
        
        return messages
    
    def normalize_project_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализация данных сообщения к единому формату проекта
        
        Args:
            message: Сообщение в формате Telegram
            
        Returns:
            Dict[str, Any]: Нормализованный проект
        """
        normalized = {
            'title': message.get('title', ''),
            'description': message.get('description', ''),
            'budget': message.get('budget'),  # Telegram обычно не содержит информации о бюджете
            'region': message.get('region', ''),
            'technologies': message.get('hashtags', []) + message.get('mentions', []),
            'url': message.get('url', ''),
            'date': message.get('date', datetime.now().isoformat()),
            'source': message.get('source', 'telegram.com'),
            'type': message.get('type', 'order'),
            'external_id': message.get('external_id', ''),
        }
        
        # Убираем дубликаты технологий и приводим к нижнему регистру
        if normalized['technologies']:
            normalized['technologies'] = list(set(tech.lower() for tech in normalized['technologies'] if tech))
        
        # Убираем пустые значения
        if not normalized['budget']:
            normalized['budget'] = None
        
        return normalized
    
    async def close(self):
        """Закрытие Telegram клиента"""
        if self.client:
            await self.client.disconnect()