import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from database import Database
from utils import format_user_link
from keyboards import get_admin_menu_keyboard

router = Router()
db = Database()
logger = logging.getLogger(__name__)


class CustomPaymentStates(StatesGroup):
    waiting_for_amount = State()


@router.message(F.text == "📊 Статистика")
async def show_statistics(message: Message) -> None:
    user_id = message.from_user.id
    
    if not Config.is_admin(user_id):
        await message.answer("❌ У вас нет прав для этого действия!")
        return
    
    try:
        stats = await db.get_statistics(days=30)
        
        text = (
            "📊 <b>Статистика за последние 30 дней</b>\n\n"
            f"✅ <b>Оплачено заявок:</b> {stats['total_paid']}\n"
            f"💰 <b>Общая сумма:</b> ${stats['total_amount']}\n"
            f"⏳ <b>Ожидает оплаты:</b> {stats['pending']}\n"
        )
        
        if stats['by_employee']:
            text += "\n<b>По сотрудникам:</b>\n"
            for emp_id, emp_data in stats['by_employee'].items():
                user_link = format_user_link(emp_id, emp_data['username'])
                text += f"  • {user_link}: {emp_data['count']} заявок (${emp_data['amount']})\n"
        
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")
        await message.answer("❌ Ошибка при получении статистики.")


@router.message(F.text == "❓ Помощь")
async def admin_help(message: Message) -> None:
    user_id = message.from_user.id
    
    if not Config.is_admin(user_id):
        return
    
    text = (
        "🔧 <b>Руководство администратора:</b>\n\n"
        "<b>📊 Основные функции:</b>\n"
        "📊 Статистика - Показать статистику за 30 дней\n"
        "👥 Управление сотрудниками - Добавить/удалить сотрудников\n\n"
        "<b>Кнопки на заявках:</b>\n"
        "✍️ <b>Отписал</b> - Отметить, что вы связались с сотрудником\n"
        "💵 <b>Оплатить 15/25</b> - Быстрая оплата\n"
        "💳 <b>Другая сумма</b> - Указать произвольную сумму оплаты\n"
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_menu_keyboard())


@router.callback_query(F.data == "back_to_admin_menu")
async def back_to_admin_menu(callback: CallbackQuery) -> None:
    """Вернуться в админ-меню"""
    if not Config.is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        "🔧 <b>Панель администратора</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("custom_pay_"))
async def custom_payment_start(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    payment_id = int(callback.data.split("_")[2])
    
    payment = await db.get_payment_by_id(payment_id)
    
    if not payment:
        await callback.answer("❌ Заявка не найдена!", show_alert=True)
        return
    
    if payment.status == "paid":
        await callback.answer("❌ Заявка уже оплачена!", show_alert=True)
        return
    
    await state.update_data(payment_id=payment_id, payment_message_id=callback.message.message_id)
    await state.set_state(CustomPaymentStates.waiting_for_amount)
    
    await callback.answer("Введите сумму оплаты")
    await callback.message.answer(
        f"💳 <b>Введите сумму оплаты для заявки #{payment_id}</b>\n\n"
        "Отправьте число (например: 30)\n\n"
        "Для отмены отправьте /cancel",
        parse_mode="HTML"
    )


@router.message(CustomPaymentStates.waiting_for_amount, F.text)
async def custom_payment_process(message: Message, state: FSMContext, bot) -> None:
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Отменено.")
        return
    
    try:
        payment_amount = int(message.text.strip())
        
        if payment_amount <= 0:
            await message.answer("❌ Сумма должна быть больше нуля. Попробуйте снова:")
            return
        
        if payment_amount > 10000:
            await message.answer("❌ Сумма слишком велика. Попробуйте снова:")
            return
        
    except ValueError:
        await message.answer("❌ Неверный формат. Введите число (например: 30):")
        return
    
    data = await state.get_data()
    payment_id = data['payment_id']
    
    payment = await db.get_payment_by_id(payment_id)
    
    if not payment:
        await message.answer("❌ Заявка не найдена!")
        await state.clear()
        return
    
    if payment.status == "paid":
        await message.answer("❌ Заявка уже оплачена!")
        await state.clear()
        return
    
    try:
        await db.update_payment_status(payment_id, "paid", payment_amount)
        
        employee_link = format_user_link(payment.employee_id, payment.employee_username)
        employee_name = await db.get_employee_name(payment.employee_id)
        await bot.send_photo(
            chat_id=Config.GROUP_CHAT_ID,
            photo=payment.screenshot_file_id,
            caption=(
                "✅ <b>Оплачено</b>\n\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
                f"💵 <b>Оплата:</b> {payment_amount}\n"
                f"👤 <b>Сотрудник:</b> {employee_link}\n"
                f"👨 <b>Имя:</b> {employee_name or 'Не указано'}"
            ),
            parse_mode="HTML"
        )
        
        try:
            employee_name = await db.get_employee_name(payment.employee_id)
            await bot.send_message(
                chat_id=payment.employee_id,
                text=(
                    f"✅ <b>Ваша заявка #{payment_id} оплачена!</b>\n\n"
                    f"👨 <b>Имя:</b> {employee_name or 'Не указано'}\n"
                    f"💵 <b>Сумма:</b> {payment_amount}\n"
                    f"🔑 <b>Юзернейм:</b> {payment.username_field}\n\n"
                    "Спасибо за работу! 🎉"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify employee: {e}")
        
        await message.answer(
            f"✅ <b>Заявка #{payment_id} оплачена на сумму {payment_amount}!</b>",
            parse_mode="HTML"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error processing custom payment: {e}")
        await message.answer("❌ Ошибка при обработке оплаты.")
        await state.clear()


@router.callback_query(F.data.startswith("replied_"))
async def process_replied(callback: CallbackQuery, bot) -> None:
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    payment_id = int(callback.data.split("_")[1])
    
    payment = await db.get_payment_by_id(payment_id)
    
    if not payment:
        await callback.answer("❌ Заявка не найдена!", show_alert=True)
        return
    
    if payment.status == "paid":
        await callback.answer("❌ Заявка уже оплачена!", show_alert=True)
        return
    
    if payment.replied:
        await callback.answer("❌ Вы уже отписали по этой заявке!", show_alert=True)
        return
    
    await db.update_payment_replied(payment_id)
    
    employee_link = format_user_link(payment.employee_id, payment.employee_username)
    employee_name = callback.bot_data.get("employees", {}).get(payment.employee_id, {}).get("full_name", "Не указано")
    await callback.message.edit_caption(
        caption=(
            f"📋 <b>Новая заявка #{payment_id}</b>\n\n"
            f"👤 <b>Сотрудник:</b> {employee_link}\n"
            f"👨 <b>Имя:</b> {employee_name}\n"
            f"💰 <b>Баланс:</b> {payment.balance}\n"
            f"🔑 <b>Юзернейм:</b> {payment.username_field}\n\n"
            f"✍️ <b>Отписал</b>"
        ),
        parse_mode="HTML",
        reply_markup=callback.message.reply_markup
    )
    
    if payment.employee_message_id:
        try:
            await bot.edit_message_caption(
                chat_id=payment.employee_id,
                message_id=payment.employee_message_id,
                caption=(
                    f"✅ <b>Заявка #{payment_id} успешно создана!</b>\n\n"
                    f"💰 <b>Баланс:</b> {payment.balance}\n"
                    f"🔑 <b>Юзернейм:</b> {payment.username_field}\n\n"
                    f"Ожидайте обработки администратором.\n\n"
                    f"✍️ <b>Отписал</b>"
                ),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Ошибка при редактировании сообщения сотрудника: {e}")
    
    await callback.answer("✅ Отмечено как 'Отписал'")


@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, bot) -> None:
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    parts = callback.data.split("_")
    payment_amount = int(parts[1])
    payment_id = int(parts[2])
    
    payment = await db.get_payment_by_id(payment_id)
    
    if not payment:
        await callback.answer("❌ Заявка не найдена!", show_alert=True)
        return
    
    if payment.status == "paid":
        await callback.answer("❌ Заявка уже оплачена!", show_alert=True)
        return
    
    await db.update_payment_status(payment_id, "paid", payment_amount)
    
    employee_link = format_user_link(payment.employee_id, payment.employee_username)
    employee_name = callback.bot_data.get("employees", {}).get(payment.employee_id, {}).get("full_name", "Не указано")
    replied_text = "\n✍️ <b>Отписал</b>" if payment.replied else ""
    await callback.message.edit_caption(
        caption=(
            f"✅ <b>Заявка #{payment_id} ОПЛАЧЕНА</b>\n\n"
            f"👤 <b>Сотрудник:</b> {employee_link}\n"
            f"👨 <b>Имя:</b> {employee_name}\n"
            f"💰 <b>Баланс:</b> {payment.balance}\n"
            f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
            f"💵 <b>Сумма оплаты:</b> {payment_amount}"
            f"{replied_text}"
        ),
        parse_mode="HTML"
    )
    
    try:
        employee_link = format_user_link(payment.employee_id, payment.employee_username)
        employee_name = callback.bot_data.get("employees", {}).get(payment.employee_id, {}).get("full_name", "Не указано")
        await bot.send_photo(
            chat_id=Config.GROUP_CHAT_ID,
            photo=payment.screenshot_file_id,
            caption=(
                "✅ <b>Оплачено</b>\n\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
                f"💵 <b>Оплата:</b> {payment_amount}\n"
                f"👤 <b>Сотрудник:</b> {employee_link}\n"
                f"👨 <b>Имя:</b> {employee_name}"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(
            f"⚠️ Заявка оплачена, но не удалось отправить в групповой чат: {str(e)}",
            show_alert=True
        )
        return
    
    try:
        employee_name = await db.get_employee_name(payment.employee_id)
        await bot.send_message(
            chat_id=payment.employee_id,
            text=(
                f"✅ <b>Ваша заявка #{payment_id} оплачена!</b>\n\n"
                f"👨 <b>Имя:</b> {employee_name or 'Не указано'}\n"
                f"💵 <b>Сумма:</b> {payment_amount}\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n\n"
                "Спасибо за работу! 🎉"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    await callback.answer(f"✅ Заявка оплачена на сумму {payment_amount}!")

