import asyncio
import logging
import signal
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import Config
from database import Database
from handlers import employee, admin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot_instance = None
db_instance = None


async def shutdown(signal_type: str = None) -> None:
    if signal_type:
        logger.info(f"Получен сигнал {signal_type}, выполняется остановка...")
    
    if bot_instance:
        try:
            await bot_instance.session.close()
            logger.info("✅ Bot session closed")
        except Exception as e:
            logger.error(f"Error closing bot session: {e}")
    
    if db_instance:
        try:
            await db_instance.close()
            logger.info("✅ Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")


async def main() -> None:
    global bot_instance, db_instance
    
    try:
        Config.validate()
        logger.info("✅ Конфигурация загружена успешно")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        return
    
    db_instance = Database()
    try:
        await db_instance.init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        return
    
    try:
        bot_instance = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        dp.include_router(employee.router)
        dp.include_router(admin.router)
        
        logger.info("🤖 Бот запущен и готов к работе!")
        
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot_instance.send_message(
                    chat_id=admin_id,
                    text="🤖 <b>Бот запущен и готов к работе!</b>",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление администратору {admin_id}: {e}")
        
        await dp.start_polling(bot_instance, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        raise
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

