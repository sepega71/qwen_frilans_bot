#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной модуль телеграм-бота для автоматического сбора, фильтрации и персонализированной рассылки актуальных заказов и вакансий для фрилансеров.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from telegram import Update, Bot, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

# Импорт менеджера настроек пользователей
from user_settings_manager import UserSettingsManager
from data_storage import DataStorage
from filter_engine import FilterEngine
from personalization_engine import PersonalizationEngine
from notification_engine import NotificationEngine
from notification_scheduler import NotificationScheduler
from user_interaction_tracker import UserInteractionTracker

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class FreelanceBot:
    """
    Основной класс телеграм-бота для фрилансеров.
    Обрабатывает команды, настройки фильтрации и отправляет уведомления.
    """
    
    def __init__(self, token: str, data_storage: DataStorage, filter_engine: FilterEngine,
                 personalization_engine: PersonalizationEngine, notification_engine: NotificationEngine,
                 notification_scheduler: NotificationScheduler, user_interaction_tracker: UserInteractionTracker):
        """
        Инициализация бота
        
        Args:
            token: Токен телеграм-бота
            data_storage: Хранилище данных
            filter_engine: Движок фильтрации
            personalization_engine: Движок персонализации
            notification_engine: Движок уведомлений
            notification_scheduler: Планировщик уведомлений
            user_interaction_tracker: Трекер взаимодействия с пользователем
        """
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self.user_settings_manager = UserSettingsManager()  # Используем новый менеджер настроек
        self.data_storage = data_storage
        self.filter_engine = filter_engine
        self.personalization_engine = personalization_engine
        self.notification_engine = notification_engine
        self.notification_scheduler = notification_scheduler
        self.user_interaction_tracker = user_interaction_tracker
        
    def register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("filter", self.filter_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        
        # Обработчик inline-кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))
        
        # Добавление дополнительных обработчиков команд
        self.application.add_handler(CommandHandler("add_keywords", add_keywords))
        self.application.add_handler(CommandHandler("remove_keywords", remove_keywords))
        self.application.add_handler(CommandHandler("add_tech", add_technologies))
        self.application.add_handler(CommandHandler("remove_tech", remove_technologies))
        self.application.add_handler(CommandHandler("set_budget", set_budget))
        self.application.add_handler(CommandHandler("set_region", set_regions))
        self.application.add_handler(CommandHandler("set_project_type", set_project_types))
        self.application.add_handler(CommandHandler("set_experience", set_experience_level))
        self.application.add_handler(CommandHandler("set_payment_type", set_payment_type))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка команды /start
        """
        user = update.effective_user
        user_id = user.id
        
        # Создание клавиатуры с основными командами
        keyboard = [
            [
                InlineKeyboardButton("Настройки", callback_data='settings'),
                InlineKeyboardButton("Фильтры", callback_data='filters')
            ],
            [
                InlineKeyboardButton("Подписаться", callback_data='subscribe'),
                InlineKeyboardButton("Отписаться", callback_data='unsubscribe')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = (
            f"Привет, {user.first_name}! 👋\n\n"
            "Я - бот для фрилансеров, который автоматически собирает, фильтрует и "
            "рассылает актуальные заказы и вакансии из различных источников.\n\n"
            "Доступные команды:\n"
            "/settings - настройка профиля и предпочтений\n"
            "/filter - настройка фильтров поиска\n"
            "/subscribe - подписаться на рассылку\n"
            "/unsubscribe - отписаться от рассылки\n"
            "/help - справка по использованию бота"
        )
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка команды /help
        """
        message = (
            "🤖 Помощь по использованию бота:\n\n"
            "🔍 Сбор заказов и вакансий:\n"
            "Бот автоматически собирает актуальные заказы и вакансии из различных источников:\n"
            "- fl.ru\n"
            "- weblancer.net\n"
            "- freemarket.ru\n"
            "- GitHub (open-source проекты)\n\n"
            "⚙️ Настройка фильтров:\n"
            "Вы можете настроить фильтры по:\n"
            "- Ключевым словам\n"
            "- Стеку технологий\n"
            "- Бюджету (минимальный/максимальный)\n"
            "- Региону выполнения\n"
            "- Типу проекта (заказ или вакансия)\n"
            "- Опыту исполнителя\n"
            "- Форме оплаты\n\n"
            "🔔 Рассылка:\n"
            "После настройки фильтров и подписки вы будете получать уведомления "
            "о новых совпадениях с вашими критериями.\n\n"
            "Для настройки используйте команду /settings и /filter"
        )
        
        await update.message.reply_text(message)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка команды /settings
        """
        user_id = update.effective_user.id
        settings = self.user_settings_manager.get_user_settings(user_id)
        
        message = (
            "⚙️ Ваши настройки:\n\n"
            f"Подписка: {'Да' if settings.subscribed else 'Нет'}\n"
            f"Ключевые слова: {', '.join(settings.filters.keywords) if settings.filters.keywords else 'Не заданы'}\n"
            f"Технологии: {', '.join(settings.filters.technologies) if settings.filters.technologies else 'Не заданы'}\n"
            f"Бюджет: {f'{settings.filters.budget_min}-{settings.filters.budget_max}' if settings.filters.budget_min or settings.filters.budget_max else 'Любой'}\n"
            f"Регионы: {', '.join(settings.filters.regions) if settings.filters.regions else 'Любые'}\n"
            f"Типы проектов: {', '.join(settings.filters.project_types) if settings.filters.project_types else 'Любые'}\n"
            f"Уровень опыта: {settings.filters.experience_level if settings.filters.experience_level else 'Любой'}\n"
            f"Форма оплаты: {settings.filters.payment_type if settings.filters.payment_type else 'Любая'}\n\n"
            "Для изменения настроек используйте команды:\n"
            "/filter - настройка фильтров поиска\n"
            "/subscribe или /unsubscribe - управление подпиской"
        )
        
        await update.message.reply_text(message)
    
    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка команды /filter
        """
        message = (
            "🔍 Настройка фильтров:\n\n"
            "Для добавления ключевых слов: /add_keywords слово1, слово2\n"
            "Для удаления ключевых слов: /remove_keywords слово1, слово2\n"
            "Для добавления технологий: /add_tech технология1, технология2\n"
            "Для удаления технологий: /remove_tech технология1, технология2\n\n"
            "Для установки бюджета: /set_budget минимальный_бюджет максимальный_бюджет\n\n"
            "Для установки региона: /set_region регион1, регион2\n\n"
            "Для установки типа проекта: /set_project_type заказ,вакансия\n\n"
            "Для установки уровня опыта: /set_experience уровень\n\n"
            "Для установки формы оплаты: /set_payment_type форма_оплаты\n\n"
            "Пример: /add_keywords python, telegram, bot"
        )
        
        await update.message.reply_text(message)
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка команды /subscribe
        """
        user_id = update.effective_user.id
        self.user_settings_manager.update_user_subscription(user_id, True)
        
        await update.message.reply_text("✅ Вы успешно подписались на рассылку актуальных заказов и вакансий!")
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка команды /unsubscribe
        """
        user_id = update.effective_user.id
        self.user_settings_manager.update_user_subscription(user_id, False)
        
        await update.message.reply_text("❌ Вы отписались от рассылки. Для повторной подписки используйте /subscribe")
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка нажатий на inline-кнопки
        """
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        settings = self.user_settings_manager.get_user_settings(user_id)
        
        if query.data == 'settings':
            message = (
                "⚙️ Ваши настройки:\n\n"
                f"Подписка: {'Да' if settings.subscribed else 'Нет'}\n"
                f"Ключевые слова: {', '.join(settings.filters.keywords) if settings.filters.keywords else 'Не заданы'}\n"
                f"Технологии: {', '.join(settings.filters.technologies) if settings.filters.technologies else 'Не заданы'}\n"
                f"Бюджет: {f'{settings.filters.budget_min}-{settings.filters.budget_max}' if settings.filters.budget_min or settings.filters.budget_max else 'Любой'}\n"
                f"Регионы: {', '.join(settings.filters.regions) if settings.filters.regions else 'Любые'}\n"
                f"Типы проектов: {', '.join(settings.filters.project_types) if settings.filters.project_types else 'Любые'}\n"
                f"Уровень опыта: {settings.filters.experience_level if settings.filters.experience_level else 'Любой'}\n"
                f"Форма оплаты: {settings.filters.payment_type if settings.filters.payment_type else 'Любая'}"
            )
            
            await query.edit_message_text(text=message)
        
        elif query.data == 'filters':
            message = (
                "🔍 Настройка фильтров:\n\n"
                "Для добавления ключевых слов: /add_keywords слово1, слово2\n"
                "Для удаления ключевых слов: /remove_keywords слово1, слово2\n\n"
                "Для добавления технологий: /add_tech технология1, технология2\n"
                "Для удаления технологий: /remove_tech технология1, технология2\n\n"
                "Для установки бюджета: /set_budget минимальный_бюджет максимальный_бюджет\n\n"
                "Для установки региона: /set_region регион1, регион2\n\n"
                "Для установки типа проекта: /set_project_type заказ,вакансия\n\n"
                "Для установки уровня опыта: /set_experience уровень\n\n"
                "Для установки формы оплаты: /set_payment_type форма_оплаты\n\n"
                "Пример: /add_keywords python, telegram, bot"
            )
            
            await query.edit_message_text(text=message)
        
        elif query.data == 'subscribe':
            self.user_settings_manager.update_user_subscription(user_id, True)
            await query.edit_message_text(text="✅ Вы успешно подписались на рассылку актуальных заказов и вакансий!")
        
        elif query.data == 'unsubscribe':
            self.user_settings_manager.update_user_subscription(user_id, False)
            await query.edit_message_text(text="❌ Вы отписались от рассылки. Для повторной подписки используйте /subscribe")
    
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Обработка текстовых сообщений
        """
        message = (
            "Я - бот для фрилансеров. Я автоматически собираю, фильтрую и "
            "рассылаю актуальные заказы и вакансии.\n\n"
            "Доступные команды:\n"
            "/start - начать работу с ботом\n"
            "/help - справка по использованию\n"
            "/settings - настройка профиля и предпочтений\n"
            "/filter - настройка фильтров поиска\n"
            "/subscribe - подписаться на рассылку\n"
            "/unsubscribe - отписаться от рассылки"
        )
        
        await update.message.reply_text(message)
    
    def run(self):
        """Запуск бота с использованием встроенного метода run_polling"""
        logger.info("Запуск телеграм-бота...")
        
        # Добавляем бота в данные приложения до регистрации обработчиков
        self.application.bot_data['bot_core'] = self
        
        # Регистрация обработчиков команд
        self.register_handlers()
        
        # Запуск бота с использованием встроенного метода
        self.application.run_polling(drop_pending_updates=True)
    
    async def send_notification(self, user_id: int, message: str):
        """
        Отправка уведомления пользователю
        
        Args:
            user_id: ID пользователя
            message: Текст уведомления
        """
        try:
            await self.application.bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Уведомление отправлено пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
    
    async def handle_project_notification_request(self, project_data: Dict[str, Any]):
        """
        Обработка запроса на отправку уведомления о новом проекте
        
        Args:
            project_data: Данные проекта для отправки
        """
        # Отправляем проект через движок персонализации и уведомлений
        results = await self.notification_engine.send_personalized_notifications_for_projects([project_data])
        logger.info(f"Отправлены уведомления о новом проекте. Результаты: {results}")
    
    async def track_user_interaction(self, user_id: int, project_id: int, interaction_type: str):
        """
        Отслеживание взаимодействия пользователя с проектом
        
        Args:
            user_id: ID пользователя
            project_id: ID проекта
            interaction_type: Тип взаимодействия
        """
        self.user_interaction_tracker.record_interaction(user_id, project_id, interaction_type)
        logger.info(f"Записано взаимодействие: пользователь {user_id}, проект {project_id}, тип {interaction_type}")


# Дополнительные функции для работы с настройками пользователя
async def add_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление ключевых слов в фильтр"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        keywords = [kw.strip() for kw in ' '.join(context.args).split(',')]
        bot_core.user_settings_manager.add_keywords(user_id, keywords)
        
        await update.message.reply_text(f"✅ Ключевые слова добавлены: {', '.join(keywords)}")
    else:
        await update.message.reply_text("❌ Укажите ключевые слова. Пример: /add_keywords python, telegram, bot")


async def remove_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление ключевых слов из фильтра"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        keywords = [kw.strip() for kw in ' '.join(context.args).split(',')]
        
        bot_core.user_settings_manager.remove_keywords(user_id, keywords)
        
        await update.message.reply_text(f"✅ Ключевые слова удалены: {', '.join(keywords)}")
    else:
        await update.message.reply_text("❌ Укажите ключевые слова для удаления. Пример: /remove_keywords python, telegram")


async def add_technologies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление технологий в фильтр"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        technologies = [tech.strip() for tech in ' '.join(context.args).split(',')]
        bot_core.user_settings_manager.add_technologies(user_id, technologies)
        
        await update.message.reply_text(f"✅ Технологии добавлены: {', '.join(technologies)}")
    else:
        await update.message.reply_text("❌ Укажите технологии. Пример: /add_tech Python, JavaScript, React")


async def remove_technologies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление технологий из фильтра"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        technologies = [tech.strip() for tech in ' '.join(context.args).split(',')]
        
        bot_core.user_settings_manager.remove_technologies(user_id, technologies)
        
        await update.message.reply_text(f"✅ Технологии удалены: {', '.join(technologies)}")
    else:
        await update.message.reply_text("❌ Укажите технологии для удаления. Пример: /remove_tech Python, JavaScript")


async def set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка диапазона бюджета"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if len(context.args) >= 2:
        try:
            min_budget = int(context.args[0])
            max_budget = int(context.args[1])
            
            if min_budget > max_budget:
                await update.message.reply_text("❌ Минимальный бюджет не может быть больше максимального")
                return
            
            bot_core.user_settings_manager.set_budget(user_id, min_budget, max_budget)
            
            await update.message.reply_text(f"✅ Бюджет установлен: {min_budget} - {max_budget}")
        except ValueError:
            await update.message.reply_text("❌ Укажите числовые значения бюджета. Пример: /set_budget 1000 5000")
    elif len(context.args) == 1:
        try:
            min_budget = int(context.args[0])
            
            bot_core.user_settings_manager.set_budget(user_id, min_budget=min_budget)
            
            await update.message.reply_text(f"✅ Минимальный бюджет установлен: {min_budget}")
        except ValueError:
            await update.message.reply_text("❌ Укажите числовые значения бюджета. Пример: /set_budget 10000 5000")
    else:
        await update.message.reply_text("❌ Укажите минимальный и/или максимальный бюджет. Пример: /set_budget 1000 50000")


async def set_regions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка регионов"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        regions = [region.strip() for region in ' '.join(context.args).split(',')]
        bot_core.user_settings_manager.set_regions(user_id, regions)
        
        await update.message.reply_text(f"✅ Регионы добавлены: {', '.join(regions)}")
    else:
        await update.message.reply_text("❌ Укажите регионы. Пример: /set_region Москва, Санкт-Петербург")


async def set_project_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка типов проектов"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        valid_types = ['заказ', 'вакансия', 'order', 'vacancy']
        project_types = [pt.strip().lower() for pt in ' '.join(context.args).split(',')]
        
        invalid_types = [pt for pt in project_types if pt not in valid_types]
        if invalid_types:
            await update.message.reply_text(f"❌ Некорректные типы проектов: {', '.join(invalid_types)}. Допустимые значения: заказ, вакансия, order, vacancy")
            return
        
        # Преобразование в стандартный формат
        normalized_types = []
        for pt in project_types:
            if pt in ['заказ', 'order']:
                normalized_types.append('order')
            elif pt in ['вакансия', 'vacancy']:
                normalized_types.append('vacancy')
        
        bot_core.user_settings_manager.set_project_types(user_id, normalized_types)
        
        type_names = {'order': 'заказ', 'vacancy': 'вакансия'}
        display_types = [type_names[pt] for pt in normalized_types]
        
        await update.message.reply_text(f"✅ Типы проектов добавлены: {', '.join(display_types)}")
    else:
        await update.message.reply_text("❌ Укажите типы проектов. Пример: /set_project_type заказ,вакансия")


async def set_experience_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка уровня опыта"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        valid_levels = ['начинающий', 'средний', 'опытный', 'эксперт', 'junior', 'middle', 'senior', 'expert']
        level = ' '.join(context.args).lower()
        
        if level not in valid_levels:
            await update.message.reply_text(f"❌ Некорректный уровень опыта. Допустимые значения: {', '.join(valid_levels)}")
            return
        
        # Преобразование в стандартный формат
        level_mapping = {
            'начинающий': 'junior',
            'средний': 'middle',
            'опытный': 'senior',
            'эксперт': 'expert'
        }
        
        normalized_level = level_mapping.get(level, level)
        bot_core.user_settings_manager.set_experience_level(user_id, normalized_level)
        
        await update.message.reply_text(f"✅ Уровень опыта установлен: {level}")
    else:
        await update.message.reply_text("❌ Укажите уровень опыта. Пример: /set_experience junior")


async def set_payment_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка формы оплаты"""
    user_id = update.effective_user.id
    bot_core = context.bot_data.get('bot_core')
    
    if not bot_core:
        await update.message.reply_text("Ошибка: бот не инициализирован")
        return
    
    if context.args:
        valid_types = ['почасовая', 'фиксированная', 'проектная', 'hourly', 'fixed', 'project']
        payment_type = ' '.join(context.args).lower()
        
        if payment_type not in valid_types:
            await update.message.reply_text(f"❌ Некорректная форма оплаты. Допустимые значения: {', '.join(valid_types)}")
            return
        
        # Преобразование в стандартный формат
        type_mapping = {
            'почасовая': 'hourly',
            'фиксированная': 'fixed',
            'проектная': 'project'
        }
        
        normalized_type = type_mapping.get(payment_type, payment_type)
        bot_core.user_settings_manager.set_payment_type(user_id, normalized_type)
        
        await update.message.reply_text(f"✅ Форма оплаты установлена: {payment_type}")
    else:
        await update.message.reply_text("❌ Укажите форму оплаты. Пример: /set_payment_type hourly")


def setup_bot_application(token: str):
    """Настройка приложения бота с дополнительными обработчиками"""
    # Создаем экземпляры всех необходимых компонентов
    data_storage = DataStorage()
    user_settings_manager = UserSettingsManager()
    filter_engine = FilterEngine()
    personalization_engine = PersonalizationEngine(user_settings_manager, filter_engine)
    user_interaction_tracker = UserInteractionTracker()
    
    # Создаем движок уведомлений
    notification_engine = NotificationEngine(
        token, user_settings_manager, data_storage, personalization_engine
    )
    
    # Создаем планировщик уведомлений
    notification_scheduler = NotificationScheduler(
        notification_engine, data_storage, personalization_engine
    )
    
    # Создаем бота с интеграцией всех компонентов
    bot_core = FreelanceBot(
        token, data_storage, filter_engine, personalization_engine,
        notification_engine, notification_scheduler, user_interaction_tracker
    )
    
    return bot_core


if __name__ == "__main__":
    import os
    from config import TELEGRAM_BOT_TOKEN
    
    # Получаем токен из переменной окружения или конфига
    token = os.getenv('TELEGRAM_BOT_TOKEN') or TELEGRAM_BOT_TOKEN
    
    if not token:
        print("Ошибка: Не указан токен телеграм-бота. Установите переменную окружения TELEGRAM_BOT_TOKEN или укажите токен в конфиге.")
    else:
        bot = setup_bot_application(token)
        print("Бот успешно настроен. Запуск...")
        bot.run()