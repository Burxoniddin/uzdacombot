"""
    Telegram event handlers
"""
import sys
import logging
from telnetlib import SE
from typing import Dict

import telegram.error
from telegram import Bot, Update, BotCommand
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler
)



from dtb.celery import app  # event processing in async mode
from dtb.settings import TELEGRAM_TOKEN, DEBUG

from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.location.static_text import BOOKS, PROGS, VIDEOS, SEARCH, BOOK_ADD, BOOK_LIST,PROG_ADD, PROG_LIST, VIDEO_ADD, VIDEO_LIST



def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))
    dp.add_handler(MessageHandler(Filters.text("Bosh Menyu"), onboarding_handlers.command_start))

    # admin commands
    dp.add_handler(CommandHandler("admin", admin_handlers.admin))
    dp.add_handler(CommandHandler("stats", admin_handlers.stats))
    dp.add_handler(CommandHandler('export_users', admin_handlers.export_users))

    # location
    dp.add_handler(CommandHandler("ask_location", location_handlers.ask_for_location))
    dp.add_handler(MessageHandler(Filters.location, location_handlers.location_handler))

    #categories
    dp.add_handler(MessageHandler(Filters.text(BOOKS), onboarding_handlers.cat_books))
    dp.add_handler(MessageHandler(Filters.text(PROGS), onboarding_handlers.cat_progs ))
    dp.add_handler(MessageHandler(Filters.text(VIDEOS),  onboarding_handlers.cat_videos))
    dp.add_handler(MessageHandler(Filters.text("Orqaga"),  onboarding_handlers.command_start))    
    dp.add_handler(MessageHandler(Filters.text(BOOK_ADD),  onboarding_handlers.add_book))
    dp.add_handler(MessageHandler(Filters.text(BOOK_LIST),  onboarding_handlers.book_list))
    dp.add_handler(MessageHandler(Filters.text(PROG_ADD),  onboarding_handlers.add_prog))
    dp.add_handler(MessageHandler(Filters.text(PROG_LIST),  onboarding_handlers.prog_list))
    dp.add_handler(MessageHandler(Filters.text(VIDEO_ADD),  onboarding_handlers.add_video))
    dp.add_handler(MessageHandler(Filters.document | Filters.video | Filters.photo,  onboarding_handlers.upload_file))  
    dp.add_handler(MessageHandler(Filters.text(VIDEO_LIST),  onboarding_handlers.video_list))
    dp.add_handler(MessageHandler(Filters.text,  onboarding_handlers.add_name))
    
    
    
    
    # dp.add_handler(MessageHandler(filters.Regex(SEARCH),  onboarding_handlers.cat_search))
    
     
    
    # secret level
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.secret_level, pattern=f"^{SECRET_LEVEL_BUTTON}"))

    # broadcast message
    dp.add_handler(
        MessageHandler(Filters.regex(rf'^{broadcast_command}(/s)?.*'), broadcast_handlers.broadcast_command_with_message)
    )
    dp.add_handler(
        CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler, pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    )

    # files
    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
    ))
    #callback_querylar uchun
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="1"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="2"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="3"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="4"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="5"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="6"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="7"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="8"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="9"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="10"))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.list_view, pattern="11"))
    
    
    
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.detail))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    #endobnoarding
    
    
    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))
 

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'en': {
            'start': 'Start django bot 🚀',
            'stats': 'Statistics of bot 📊',
            'admin': 'Show admin info ℹ️',
            'ask_location': 'Send location 📍',
            'broadcast': 'Broadcast message 📨',
            'export_users': 'Export users.csv 👥',
        },
        'es': {
            'start': 'Iniciar el bot de django 🚀',
            'stats': 'Estadísticas de bot 📊',
            'admin': 'Mostrar información de administrador ℹ️',
            'ask_location': 'Enviar ubicación 📍',
            'broadcast': 'Mensaje de difusión 📨',
            'export_users': 'Exportar users.csv 👥',
        },
        'fr': {
            'start': 'Démarrer le bot Django 🚀',
            'stats': 'Statistiques du bot 📊',
            'admin': "Afficher les informations d'administrateur ℹ️",
            'ask_location': 'Envoyer emplacement 📍',
            'broadcast': 'Message de diffusion 📨',
            "export_users": 'Exporter users.csv 👥',
        },
        'ru': {
            'start': 'Запустить django бота 🚀',
            'stats': 'Статистика бота 📊',
            'admin': 'Показать информацию для админов ℹ️',
            'broadcast': 'Отправить сообщение 📨',
            'ask_location': 'Отправить локацию 📍',
            'export_users': 'Экспорт users.csv 👥',
        }
    }

    bot_instance.delete_my_commands()
    for language_code in langs_with_commands:
        bot_instance.set_my_commands(
            language_code=language_code,
            commands=[
                BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
            ]
        )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)

n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
