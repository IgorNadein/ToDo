"""
Telegram Bot for ToDo List application.
Uses Aiogram 3.x and Aiogram-Dialog for dialog management.
"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram_dialog import setup_dialogs

from handlers import router
from dialogs import dialog_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot."""
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        sys.exit(1)

    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Register routers
    dp.include_router(router)
    dp.include_router(dialog_router)

    # Setup dialogs
    setup_dialogs(dp)

    logger.info("Starting bot...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
