from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import Config
from database import Database

# Create router for administrator
router = Router()
db = Database()


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
    await callback.message.edit_caption(
        caption=(
            f"✅ <b>Заявка #{payment_id} ОПЛАЧЕНА</b>\n\n"
            f"👤 <b>Сотрудник:</b> @{payment.employee_username or 'Без юзернейма'}\n"
            f"💰 <b>Баланс:</b> {payment.balance}\n"
            f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
            f"💵 <b>Сумма оплаты:</b> {payment_amount}\n"
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

