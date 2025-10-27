#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Слой хранения данных.
Хранит профили пользователей, собранные заказы и вакансии.
Обеспечивает быстрый доступ к данным для фильтрации.
"""

import json
import sqlite3
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import contextmanager


class DataStorage:
    """
    Класс для хранения данных в SQLite базе данных.
    """
    
    def __init__(self, db_path: str = "frilans_bot.db"):
        """
        Инициализация слоя хранения данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    subscribed BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Таблица настроек пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    keywords TEXT,
                    technologies TEXT,
                    budget_min INTEGER,
                    budget_max INTEGER,
                    regions TEXT,
                    project_types TEXT,
                    experience_level TEXT,
                    payment_type TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Таблица проектов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    external_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT,
                    budget INTEGER,
                    region TEXT,
                    technologies TEXT,
                    url TEXT,
                    date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    type TEXT NOT NULL
                )
            """)
            
            # Таблица просмотренных проектов пользователями
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_seen_projects (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    project_id INTEGER,
                    seen_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    UNIQUE(user_id, project_id)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения к базе данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Для доступа к колонкам по имени
        try:
            yield conn
        finally:
            conn.close()
    
    def save_user(self, user_data: Dict[str, Any]) -> int:
        """
        Сохранение или обновление данных пользователя
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            int: ID пользователя в базе данных
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_data['telegram_id'],))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Обновляем существующего пользователя
                cursor.execute("""
                    UPDATE users 
                    SET subscribed = ?, updated_at = ? 
                    WHERE telegram_id = ?
                """, (
                    user_data.get('subscribed', False),
                    datetime.now().isoformat(),
                    user_data['telegram_id']
                ))
                user_id = existing_user['id']
            else:
                # Создаем нового пользователя
                cursor.execute("""
                    INSERT INTO users (telegram_id, subscribed, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_data['telegram_id'],
                    user_data.get('subscribed', False),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                user_id = cursor.lastrowid
            
            conn.commit()
            
            # Сохраняем настройки пользователя
            self.save_user_settings(user_id, user_data.get('filters', {}))
            
            return user_id
    
    def save_user_settings(self, user_id: int, filters: Dict[str, Any]):
        """
        Сохранение настроек пользователя
        
        Args:
            user_id: ID пользователя в базе данных
            filters: Настройки фильтров
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Преобразуем списки в строки для хранения
            keywords_str = ','.join(filters.get('keywords', [])) if filters.get('keywords') else None
            technologies_str = ','.join(filters.get('technologies', [])) if filters.get('technologies') else None
            regions_str = ','.join(filters.get('regions', [])) if filters.get('regions') else None
            project_types_str = ','.join(filters.get('project_types', [])) if filters.get('project_types') else None
            
            # Проверяем, существуют ли настройки
            cursor.execute("SELECT id FROM user_settings WHERE user_id = ?", (user_id,))
            existing_settings = cursor.fetchone()
            
            if existing_settings:
                # Обновляем существующие настройки
                cursor.execute("""
                    UPDATE user_settings 
                    SET keywords = ?, technologies = ?, budget_min = ?, budget_max = ?, 
                        regions = ?, project_types = ?, experience_level = ?, payment_type = ?
                    WHERE user_id = ?
                """, (
                    keywords_str, technologies_str,
                    filters.get('budget_min'), filters.get('budget_max'),
                    regions_str, project_types_str,
                    filters.get('experience_level'), filters.get('payment_type'),
                    user_id
                ))
            else:
                # Создаем новые настройки
                cursor.execute("""
                    INSERT INTO user_settings 
                    (user_id, keywords, technologies, budget_min, budget_max, 
                     regions, project_types, experience_level, payment_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, keywords_str, technologies_str,
                    filters.get('budget_min'), filters.get('budget_max'),
                    regions_str, project_types_str,
                    filters.get('experience_level'), filters.get('payment_type')
                ))
            
            conn.commit()
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение пользователя по Telegram ID
        
        Args:
            telegram_id: ID пользователя в Telegram
            
        Returns:
            Optional[Dict[str, Any]]: Данные пользователя или None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.*, us.keywords, us.technologies, us.budget_min, us.budget_max,
                       us.regions, us.project_types, us.experience_level, us.payment_type
                FROM users u
                LEFT JOIN user_settings us ON u.id = us.user_id
                WHERE u.telegram_id = ?
            """, (telegram_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Преобразуем строку с ключевыми словами обратно в список
            keywords = row['keywords'].split(',') if row['keywords'] else []
            technologies = row['technologies'].split(',') if row['technologies'] else []
            regions = row['regions'].split(',') if row['regions'] else []
            project_types = row['project_types'].split(',') if row['project_types'] else []
            
            return {
                'id': row['id'],
                'telegram_id': row['telegram_id'],
                'subscribed': bool(row['subscribed']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'filters': {
                    'keywords': keywords,
                    'technologies': technologies,
                    'budget_min': row['budget_min'],
                    'budget_max': row['budget_max'],
                    'regions': regions,
                    'project_types': project_types,
                    'experience_level': row['experience_level'],
                    'payment_type': row['payment_type']
                }
            }
    
    def save_project(self, project_data: Dict[str, Any]) -> int:
        """
        Сохранение проекта в базу данных
        
        Args:
            project_data: Данные проекта
            
        Returns:
            int: ID проекта в базе данных
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Преобразуем список технологий в строку для хранения
            technologies_str = ','.join(project_data.get('technologies', [])) if project_data.get('technologies') else None
            
            try:
                cursor.execute("""
                    INSERT INTO projects 
                    (external_id, title, description, budget, region, technologies, url, date, source, type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_data.get('external_id'),
                    project_data.get('title', ''),
                    project_data.get('description', ''),
                    project_data.get('budget'),
                    project_data.get('region', ''),
                    technologies_str,
                    project_data.get('url', ''),
                    project_data.get('date', datetime.now().isoformat()),
                    project_data.get('source', ''),
                    project_data.get('type', 'order')
                ))
                
                project_id = cursor.lastrowid
                conn.commit()
                
                return project_id
            except sqlite3.IntegrityError:
                # Проект с таким external_id уже существует
                cursor.execute("SELECT id FROM projects WHERE external_id = ?", (project_data.get('external_id'),))
                row = cursor.fetchone()
                return row['id'] if row else -1
    
    def get_recent_projects(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получение последних проектов
        
        Args:
            limit: Максимальное количество проектов
            
        Returns:
            List[Dict[str, Any]]: Список проектов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM projects 
                ORDER BY date DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            
            projects = []
            for row in rows:
                # Преобразуем строку с технологиями обратно в список
                technologies = row['technologies'].split(',') if row['technologies'] else []
                
                projects.append({
                    'id': row['id'],
                    'external_id': row['external_id'],
                    'title': row['title'],
                    'description': row['description'],
                    'budget': row['budget'],
                    'region': row['region'],
                    'technologies': technologies,
                    'url': row['url'],
                    'date': row['date'],
                    'source': row['source'],
                    'type': row['type']
                })
            
            return projects
    
    def mark_project_as_seen(self, user_id: int, project_id: int):
        """
        Отметка проекта как просмотренного пользователем
        
        Args:
            user_id: ID пользователя
            project_id: ID проекта
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO user_seen_projects (user_id, project_id, seen_at)
                VALUES (?, ?, ?)
            """, (user_id, project_id, datetime.now().isoformat()))
            
            conn.commit()
    
    def get_unseen_projects_for_user(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получение непросмотренных проектов для пользователя
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество проектов
            
        Returns:
            List[Dict[str, Any]]: Список непросмотренных проектов
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.* FROM projects p
                LEFT JOIN user_seen_projects usp ON p.id = usp.project_id AND usp.user_id = ?
                WHERE usp.id IS NULL
                ORDER BY p.date DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            
            projects = []
            for row in rows:
                # Преобразуем строку с технологиями обратно в список
                technologies = row['technologies'].split(',') if row['technologies'] else []
                
                projects.append({
                    'id': row['id'],
                    'external_id': row['external_id'],
                    'title': row['title'],
                    'description': row['description'],
                    'budget': row['budget'],
                    'region': row['region'],
                    'technologies': technologies,
                    'url': row['url'],
                    'date': row['date'],
                    'source': row['source'],
                    'type': row['type']
                })
            
            return projects
    
    def get_subscribed_users(self) -> List[Dict[str, Any]]:
        """
        Получение всех подписанных пользователей
        
        Returns:
            List[Dict[str, Any]]: Список подписанных пользователей
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT u.*, us.keywords, us.technologies, us.budget_min, us.budget_max,
                       us.regions, us.project_types, us.experience_level, us.payment_type
                FROM users u
                LEFT JOIN user_settings us ON u.id = us.user_id
                WHERE u.subscribed = 1
            """)
            
            rows = cursor.fetchall()
            
            users = []
            for row in rows:
                # Преобразуем строку с ключевыми словами обратно в список
                keywords = row['keywords'].split(',') if row['keywords'] else []
                technologies = row['technologies'].split(',') if row['technologies'] else []
                regions = row['regions'].split(',') if row['regions'] else []
                project_types = row['project_types'].split(',') if row['project_types'] else []
                
                users.append({
                    'id': row['id'],
                    'telegram_id': row['telegram_id'],
                    'subscribed': bool(row['subscribed']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'filters': {
                        'keywords': keywords,
                        'technologies': technologies,
                        'budget_min': row['budget_min'],
                        'budget_max': row['budget_max'],
                        'regions': regions,
                        'project_types': project_types,
                        'experience_level': row['experience_level'],
                        'payment_type': row['payment_type']
                    }
                })
            
            return users