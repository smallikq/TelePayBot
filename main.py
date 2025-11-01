import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config
from database import Database
from handlers import employee, admin

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot"""
    
    # Configuration validation
    try:
        Config.validate()
        logger.info("✅ Конфигурация загружена успешно")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Database initialization
    db = Database()
    await db.init_db()
    logger.info("✅ База данных инициализирована")
    
    # Create bot and dispatcher
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(employee.router)
    dp.include_router(admin.router)
    
    logger.info("🤖 Бот запущен и готов к работе!")
    
    # Send notification to all administrators about launch
    for admin_id in Config.ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🤖 <b>Бот запущен и готов к работе!</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление администратору {admin_id}: {e}")
    
    # Start polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

