import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import Config
from database import Database

# Create router for administrator
router = Router()
db = Database()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("replied_"))
async def process_replied(callback: CallbackQuery, bot):
    """Handle admin replied action"""
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    # Parse callback_data: replied_123
    payment_id = int(callback.data.split("_")[1])
    
    # Get payment request information
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
    
    # Update replied status in database
    await db.update_payment_replied(payment_id)
    
    # Update administrator's message with "Отписал" note
    await callback.message.edit_caption(
        caption=(
            f"📋 <b>Новая заявка #{payment_id}</b>\n\n"
            f"👤 <b>Сотрудник:</b> @{payment.employee_username or 'Без юзернейма'}\n"
            f"💰 <b>Баланс:</b> {payment.balance}\n"
            f"🔑 <b>Юзернейм:</b> {payment.username_field}\n\n"
            f"✍️ <b>Отписал</b>"
        ),
        parse_mode="HTML",
        reply_markup=callback.message.reply_markup
    )
    
    # Edit employee's message with "Отписал" note
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
async def process_payment(callback: CallbackQuery, bot):
    """Handle payment processing by administrator"""
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    # Parse callback_data: pay_15_123 or pay_25_123
    parts = callback.data.split("_")
    payment_amount = int(parts[1])  # 15 or 25
    payment_id = int(parts[2])
    
    # Get payment request information
    payment = await db.get_payment_by_id(payment_id)
    
    if not payment:
        await callback.answer("❌ Заявка не найдена!", show_alert=True)
        return
    
    if payment.status == "paid":
        await callback.answer("❌ Заявка уже оплачена!", show_alert=True)
        return
    
    # Update status in database
    await db.update_payment_status(payment_id, "paid", payment_amount)
    
    # Update administrator's message
    replied_text = "\n✍️ <b>Отписал</b>" if payment.replied else ""
    await callback.message.edit_caption(
        caption=(
            f"✅ <b>Заявка #{payment_id} ОПЛАЧЕНА</b>\n\n"
            f"👤 <b>Сотрудник:</b> @{payment.employee_username or 'Без юзернейма'}\n"
            f"💰 <b>Баланс:</b> {payment.balance}\n"
            f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
            f"💵 <b>Сумма оплаты:</b> {payment_amount}"
            f"{replied_text}"
        ),
        parse_mode="HTML"
    )
    
    # Send notification to group chat
    try:
        await bot.send_photo(
            chat_id=Config.GROUP_CHAT_ID,
            photo=payment.screenshot_file_id,
            caption=(
                "✅ <b>Оплачено</b>\n\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
                f"💵 <b>Оплата:</b> {payment_amount}\n"
                f"👤 <b>Сотрудник:</b> @{payment.employee_username or 'Без юзернейма'}"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(
            f"⚠️ Заявка оплачена, но не удалось отправить в групповой чат: {str(e)}",
            show_alert=True
        )
        return
    
    # Send notification to employee
    try:
        await bot.send_message(
            chat_id=payment.employee_id,
            text=(
                f"✅ <b>Ваша заявка #{payment_id} оплачена!</b>\n\n"
                f"💵 <b>Сумма:</b> {payment_amount}\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n\n"
                "Спасибо за работу! 🎉"
            ),
            parse_mode="HTML"
        )
    except Exception:
        # If we couldn't send to employee, it's okay
        pass
    
    await callback.answer(f"✅ Заявка оплачена на сумму {payment_amount}!")

