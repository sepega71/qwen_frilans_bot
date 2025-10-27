#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для тестирования ядра телеграм-бота.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes

from bot_core import FreelanceBot
from data_storage import DataStorage
from filter_engine import FilterEngine
from personalization_engine import PersonalizationEngine
from notification_engine import NotificationEngine
from notification_scheduler import NotificationScheduler
from user_interaction_tracker import UserInteractionTracker
from user_settings_manager import UserSettingsManager


class TestFreelanceBot(unittest.TestCase):
    """Тесты для ядра телеграм-бота"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Создаем моки для всех зависимостей
        self.mock_data_storage = MagicMock(spec=DataStorage)
        self.mock_filter_engine = MagicMock(spec=FilterEngine)
        self.mock_personalization_engine = MagicMock(spec=PersonalizationEngine)
        self.mock_notification_engine = MagicMock(spec=NotificationEngine)
        self.mock_notification_scheduler = MagicMock(spec=NotificationScheduler)
        self.mock_user_interaction_tracker = MagicMock(spec=UserInteractionTracker)

        # Создаем бота с моками
        self.bot = FreelanceBot(
            token="test_token",
            data_storage=self.mock_data_storage,
            filter_engine=self.mock_filter_engine,
            personalization_engine=self.mock_personalization_engine,
            notification_engine=self.mock_notification_engine,
            notification_scheduler=self.mock_notification_scheduler,
            user_interaction_tracker=self.mock_user_interaction_tracker
        )

        # Создаем фиктивные объекты для тестирования
        self.user = User(id=123456, first_name="Test", is_bot=False)
        self.chat = Chat(id=654321, type="private")
        self.message = Message(
            message_id=1,
            date=None,
            chat=self.chat,
            from_user=self.user
        )
        self.update = Update(update_id=1, message=self.message)

        # Создаем контекст
        self.context = ContextTypes.DEFAULT_TYPE

    @patch('bot_core.update_user_subscription')
    async def test_start_command(self, mock_update_subscription):
        """Тест команды /start"""
        # Подготовка
        self.update.message.text = "/start"
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.start_command(self.update, self.context)

        # Проверка
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("Привет, Test!", kwargs['text'])
        self.assertEqual(kwargs['chat_id'], self.user.id)

    @patch('bot_core.UserSettingsManager')
    async def test_help_command(self, mock_user_settings_manager):
        """Тест команды /help"""
        # Подготовка
        self.update.message.text = "/help"
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.help_command(self.update, self.context)

        # Проверка
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("🤖 Помощь по использованию бота:", kwargs['text'])
        self.assertEqual(kwargs['chat_id'], self.user.id)

    @patch('bot_core.UserSettingsManager')
    async def test_settings_command(self, mock_user_settings_manager):
        """Тест команды /settings"""
        # Подготовка
        self.update.message.text = "/settings"
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Мокаем настройки пользователя
        mock_settings = MagicMock()
        mock_settings.subscribed = True
        mock_settings.filters.keywords = ["python", "telegram"]
        mock_settings.filters.technologies = ["Python", "JavaScript"]
        mock_settings.filters.budget_min = 1000
        mock_settings.filters.budget_max = 5000
        mock_settings.filters.regions = ["Москва", "Санкт-Петербург"]
        mock_settings.filters.project_types = ["order"]
        mock_settings.filters.experience_level = "middle"
        mock_settings.filters.payment_type = "fixed"

        self.bot.user_settings_manager.get_user_settings = MagicMock(return_value=mock_settings)

        # Выполнение
        await self.bot.settings_command(self.update, self.context)

        # Проверка
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("⚙️ Ваши настройки:", kwargs['text'])
        self.assertIn("Подписка: Да", kwargs['text'])
        self.assertIn("Ключевые слова: python, telegram", kwargs['text'])
        self.assertEqual(kwargs['chat_id'], self.user.id)

    @patch('bot_core.UserSettingsManager')
    async def test_filter_command(self, mock_user_settings_manager):
        """Тест команды /filter"""
        # Подготовка
        self.update.message.text = "/filter"
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.filter_command(self.update, self.context)

        # Проверка
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("🔍 Настройка фильтров:", kwargs['text'])
        self.assertEqual(kwargs['chat_id'], self.user.id)

    @patch('bot_core.UserSettingsManager')
    async def test_subscribe_command(self, mock_user_settings_manager):
        """Тест команды /subscribe"""
        # Подготовка
        self.update.message.text = "/subscribe"
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.subscribe_command(self.update, self.context)

        # Проверка
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("✅ Вы успешно подписались", kwargs['text'])
        self.assertEqual(kwargs['chat_id'], self.user.id)

        # Проверяем, что вызван метод обновления подписки
        self.bot.user_settings_manager.update_user_subscription.assert_called_once_with(self.user.id, True)

    @patch('bot_core.UserSettingsManager')
    async def test_unsubscribe_command(self, mock_user_settings_manager):
        """Тест команды /unsubscribe"""
        # Подготовка
        self.update.message.text = "/unsubscribe"
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.unsubscribe_command(self.update, self.context)

        # Проверка
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("❌ Вы отписались", kwargs['text'])
        self.assertEqual(kwargs['chat_id'], self.user.id)

        # Проверяем, что вызван метод обновления подписки
        self.bot.user_settings_manager.update_user_subscription.assert_called_once_with(self.user.id, False)

    async def test_send_notification(self):
        """Тест отправки уведомления пользователю"""
        # Подготовка
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.send_notification(self.user.id, "Тестовое уведомление")

        # Проверка
        self.context.bot.send_message.assert_called_once_with(
            chat_id=self.user.id,
            text="Тестовое уведомление"
        )

    async def test_handle_project_notification_request(self):
        """Тест обработки запроса на отправку уведомления о проекте"""
        # Подготовка
        project_data = {
            'title': 'Тестовый проект',
            'description': 'Описание тестового проекта',
            'budget': 10000,
            'url': 'https://example.com/project/1'
        }
        self.mock_notification_engine.send_personalized_notifications_for_projects = AsyncMock(return_value=[1])

        # Выполнение
        await self.bot.handle_project_notification_request(project_data)

        # Проверка
        self.mock_notification_engine.send_personalized_notifications_for_projects.assert_called_once_with([project_data])

    async def test_track_user_interaction(self):
        """Тест отслеживания взаимодействия пользователя с проектом"""
        # Подготовка
        user_id = 123456
        project_id = "project_123"
        interaction_type = "view"

        # Выполнение
        await self.bot.track_user_interaction(user_id, project_id, interaction_type)

        # Проверка
        self.mock_user_interaction_tracker.record_interaction.assert_called_once_with(user_id, project_id, interaction_type)


class TestBotCoreFunctions(unittest.TestCase):
    """Тесты для дополнительных функций ядра бота"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.user = User(id=123456, first_name="Test", is_bot=False)
        self.chat = Chat(id=654321, type="private")
        self.message = Message(
            message_id=1,
            date=None,
            chat=self.chat,
            from_user=self.user
        )
        self.update = Update(update_id=1, message=self.message)
        self.context = ContextTypes.DEFAULT_TYPE

    @patch('bot_core.UserSettingsManager')
    async def test_add_keywords(self, mock_user_settings_manager):
        """Тест добавления ключевых слов"""
        # Подготовка
        self.context.args = ["python", "telegram", "bot"]
        self.context.bot_data = {'bot_core': MagicMock()}
        mock_bot_core = self.context.bot_data['bot_core']
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.add_keywords(self.update, self.context)

        # Проверка
        mock_bot_core.user_settings_manager.add_keywords.assert_called_once_with(
            self.user.id,
            ["python", "telegram", "bot"]
        )
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("✅ Ключевые слова добавлены: python, telegram, bot", kwargs['text'])

    @patch('bot_core.UserSettingsManager')
    async def test_remove_keywords(self, mock_user_settings_manager):
        """Тест удаления ключевых слов"""
        # Подготовка
        self.context.args = ["python", "old_keyword"]
        self.context.bot_data = {'bot_core': MagicMock()}
        mock_bot_core = self.context.bot_data['bot_core']
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.remove_keywords(self.update, self.context)

        # Проверка
        mock_bot_core.user_settings_manager.remove_keywords.assert_called_once_with(
            self.user.id,
            ["python", "old_keyword"]
        )
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("✅ Ключевые слова удалены: python, old_keyword", kwargs['text'])

    @patch('bot_core.UserSettingsManager')
    async def test_set_budget(self, mock_user_settings_manager):
        """Тест установки бюджета"""
        # Подготовка
        self.context.args = ["1000", "5000"]
        self.context.bot_data = {'bot_core': MagicMock()}
        mock_bot_core = self.context.bot_data['bot_core']
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.set_budget(self.update, self.context)

        # Проверка
        mock_bot_core.user_settings_manager.set_budget.assert_called_once_with(
            self.user.id,
            1000,
            5000
        )
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("✅ Бюджет установлен: 1000 - 5000", kwargs['text'])

    @patch('bot_core.UserSettingsManager')
    async def test_set_regions(self, mock_user_settings_manager):
        """Тест установки регионов"""
        # Подготовка
        self.context.args = ["Москва", "Санкт-Петербург"]
        self.context.bot_data = {'bot_core': MagicMock()}
        mock_bot_core = self.context.bot_data['bot_core']
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.set_regions(self.update, self.context)

        # Проверка
        mock_bot_core.user_settings_manager.set_regions.assert_called_once_with(
            self.user.id,
            ["Москва", "Санкт-Петербург"]
        )
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("✅ Регионы добавлены: Москва, Санкт-Петербург", kwargs['text'])

    @patch('bot_core.UserSettingsManager')
    async def test_set_project_types(self, mock_user_settings_manager):
        """Тест установки типов проектов"""
        # Подготовка
        self.context.args = ["заказ", "вакансия"]
        self.context.bot_data = {'bot_core': MagicMock()}
        mock_bot_core = self.context.bot_data['bot_core']
        self.context.bot = AsyncMock()
        self.context.bot.send_message = AsyncMock()

        # Выполнение
        await self.bot.set_project_types(self.update, self.context)

        # Проверка
        mock_bot_core.user_settings_manager.set_project_types.assert_called_once_with(
            self.user.id,
            ["order", "vacancy"]
        )
        self.context.bot.send_message.assert_called_once()
        args, kwargs = self.context.bot.send_message.call_args
        self.assertIn("✅ Типы проектов добавлены: заказ, вакансия", kwargs['text'])


if __name__ == '__main__':
    # Запуск тестов
    unittest.main()