import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from database import Database
from models import Payment
from utils import Validator, RateLimiter
from keyboards import (
    get_main_menu_keyboard,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_payment_actions_keyboard,
    get_admin_payment_keyboard
)

# Create router for employees
router = Router()
db = Database()
rate_limiter = RateLimiter()
logger = logging.getLogger(__name__)


class PaymentStates(StatesGroup):
    """FSM states for payment request creation"""
    waiting_for_screenshot = State()
    waiting_for_balance = State()
    waiting_for_username = State()
    confirming = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handler for /start command"""
    user_id = message.from_user.id
    
    if not Config.is_employee(user_id):
        await message.answer(
            "❌ <b>Доступ запрещен</b>\n\n"
            "Вы не являетесь сотрудником.\n"
            "Обратитесь к администратору для получения доступа.",
            parse_mode="HTML"
        )
        return
    
    username = message.from_user.username or "Без юзернейма"
    await message.answer(
        f"👋 <b>Добро пожаловать, @{username}!</b>\n\n"
        "🤖 Я бот для подачи заявок на оплату.\n\n"
        "<b>Доступные команды:</b>\n"
        "📝 <b>Создать заявку</b> - отправить новую заявку на оплату\n"
        "📋 <b>Мои заявки</b> - посмотреть активные заявки\n\n"
        "Выберите действие из меню ниже 👇",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "📝 Создать заявку")
async def start_payment_creation(message: Message, state: FSMContext):
    """Start payment request creation"""
    user_id = message.from_user.id
    
    if not Config.is_employee(user_id):
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    # Rate limiting check
    if not rate_limiter.check_rate_limit(user_id, max_requests=3, time_window=300):
        await message.answer(
            "⚠️ <b>Слишком много запросов</b>\n\n"
            "Подождите несколько минут перед созданием новой заявки.",
            parse_mode="HTML"
        )
        return
    
    try:
        await state.set_state(PaymentStates.waiting_for_screenshot)
        await message.answer(
            "📸 <b>Шаг 1/3: Скриншот</b>\n\n"
            "Отправьте скриншот (фото).\n\n"
            "Для отмены нажмите кнопку ниже.",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
    except Exception as e:
        logger.error(f"Error starting payment creation for user {user_id}: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(StateFilter(PaymentStates.waiting_for_screenshot), F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    """Process screenshot"""
    # Save file_id of the largest photo
    photo_file_id = message.photo[-1].file_id
    await state.update_data(screenshot_file_id=photo_file_id)
    
    await state.set_state(PaymentStates.waiting_for_balance)
    await message.answer(
        "💰 <b>Шаг 2/3: Баланс</b>\n\n"
        "Отправьте информацию о балансе.\n\n"
        "Пример: 100$",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(PaymentStates.waiting_for_screenshot))
async def invalid_screenshot(message: Message):
    """Handle invalid screenshot format"""
    await message.answer(
        "❌ Пожалуйста, отправьте фото (скриншот).\n\n"
        "Используйте функцию отправки фото в Telegram.",
        parse_mode="HTML"
    )


@router.message(StateFilter(PaymentStates.waiting_for_balance), F.text, ~F.text.in_(["❌ Отменить"]))
async def process_balance(message: Message, state: FSMContext):
    """Process balance"""
    balance = message.text.strip()
    
    # Validate balance
    is_valid, error_msg = Validator.validate_balance(balance)
    if not is_valid:
        await message.answer(
            f"❌ <b>Ошибка валидации:</b> {error_msg}\n\n"
            "Попробуйте ещё раз. Пример: 100$",
            parse_mode="HTML"
        )
        return
    
    # Sanitize for safety
    balance = Validator.sanitize_html(balance)
    await state.update_data(balance=balance)
    
    await state.set_state(PaymentStates.waiting_for_username)
    await message.answer(
        "🔑 <b>Шаг 3/3: Юзернейм</b>\n\n"
        "Отправьте юзернейм.\n\n"
        "Пример: @username или username",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(PaymentStates.waiting_for_username), F.text, ~F.text.in_(["❌ Отменить"]))
async def process_username(message: Message, state: FSMContext):
    """Process username and show preview"""
    username = message.text.strip()
    
    # Validate username
    is_valid, error_msg = Validator.validate_username(username)
    if not is_valid:
        await message.answer(
            f"❌ <b>Ошибка валидации:</b> {error_msg}\n\n"
            "Попробуйте ещё раз. Пример: @username",
            parse_mode="HTML"
        )
        return
    
    # Format and sanitize username
    username = Validator.format_username(username)
    username = Validator.sanitize_html(username)
    await state.update_data(username_field=username)
    
    # Get all data
    data = await state.get_data()
    
    await state.set_state(PaymentStates.confirming)
    
    # Send preview with photo
    try:
        await message.answer_photo(
            photo=data['screenshot_file_id'],
            caption=(
                "✅ <b>Проверьте данные заявки:</b>\n\n"
                f"💰 <b>Баланс:</b> {data['balance']}\n"
                f"🔑 <b>Юзернейм:</b> {data['username_field']}\n\n"
                "Подтвердите отправку заявки:"
            ),
            parse_mode="HTML",
            reply_markup=get_confirm_keyboard()
        )
    except Exception as e:
        logger.error(f"Error showing preview for user {message.from_user.id}: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте снова.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()


@router.callback_query(F.data == "confirm_payment", StateFilter(PaymentStates.confirming))
async def confirm_payment(callback: CallbackQuery, state: FSMContext, bot):
    """Confirm and create payment request"""
    data = await state.get_data()
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    try:
        # Create payment request
        payment = Payment(
            employee_id=user_id,
            employee_username=username,
            balance=data['balance'],
            username_field=data['username_field'],
            screenshot_file_id=data['screenshot_file_id']
        )
        
        payment_id = await db.create_payment(payment)
        
        # Send to all administrators
        admin_success = False
        for admin_id in Config.ADMIN_IDS:
            try:
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=data['screenshot_file_id'],
                    caption=(
                        f"📋 <b>Новая заявка #{payment_id}</b>\n\n"
                        f"👤 <b>Сотрудник:</b> @{username or 'Без юзернейма'}\n"
                        f"💰 <b>Баланс:</b> {data['balance']}\n"
                        f"🔑 <b>Юзернейм:</b> {data['username_field']}\n"
                    ),
                    parse_mode="HTML",
                    reply_markup=get_admin_payment_keyboard(payment_id)
                )
                admin_success = True
            except Exception as e:
                logger.error(f"Error sending notification to admin {admin_id}: {e}")
        
        if not admin_success:
            await callback.answer(
                "⚠️ Не удалось отправить уведомление администраторам. Обратитесь к администратору.",
                show_alert=True
            )
            return
        
        # Edit message at employee chat and save message_id
        edited_message = await callback.message.edit_caption(
            caption=(
                f"✅ <b>Заявка #{payment_id} успешно создана!</b>\n\n"
                f"💰 <b>Баланс:</b> {data['balance']}\n"
                f"🔑 <b>Юзернейм:</b> {data['username_field']}\n\n"
                "Ожидайте обработки администратором."
            ),
            parse_mode="HTML"
        )
        
        # Save employee message_id to database
        await db.update_employee_message_id(payment_id, edited_message.message_id)
        
        await callback.answer("✅ Заявка отправлена!")
        await state.clear()
        
        # Return to main menu
        await callback.message.answer(
            "Выберите действие:",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error confirming payment for user {user_id}: {e}")
        await callback.answer(
            "❌ Произошла ошибка при создании заявки. Попробуйте позже.",
            show_alert=True
        )
        await state.clear()


@router.callback_query(F.data == "cancel_payment", StateFilter(PaymentStates.confirming))
async def cancel_payment_confirm(callback: CallbackQuery, state: FSMContext):
    """Cancel payment request creation at confirmation stage"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "❌ Создание заявки отменено.",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.message(F.text == "❌ Отменить", StateFilter("*"))
async def cancel_operation(message: Message, state: FSMContext):
    """Cancel operation"""
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer(
        "❌ Операция отменена.",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "📋 Мои заявки")
async def show_my_payments(message: Message):
    """Show user's active payment requests"""
    user_id = message.from_user.id
    
    if not Config.is_employee(user_id):
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    payments = await db.get_user_pending_payments(user_id)
    
    if not payments:
        await message.answer(
            "📋 <b>Ваши заявки</b>\n\n"
            "У вас нет активных заявок.\n\n"
            "Создайте новую заявку через меню.",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    await message.answer(
        f"📋 <b>Ваши активные заявки ({len(payments)}):</b>\n\n"
        "Нажмите на кнопку под заявкой для действий.",
        parse_mode="HTML"
    )
    
    for payment in payments:
        created_at = payment.created_at.strftime("%d.%m.%Y %H:%M")
        replied_text = "\n✍️ <b>Отписал</b>" if payment.replied else ""
        await message.answer_photo(
            photo=payment.screenshot_file_id,
            caption=(
                f"📋 <b>Заявка #{payment.id}</b>\n"
                f"📅 <b>Создана:</b> {created_at}\n\n"
                f"💰 <b>Баланс:</b> {payment.balance}\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
                f"📊 <b>Статус:</b> ⏳ Ожидает обработки"
                f"{replied_text}"
            ),
            parse_mode="HTML",
            reply_markup=get_payment_actions_keyboard(payment.id)
        )


@router.callback_query(F.data.startswith("delete_"))
async def delete_payment(callback: CallbackQuery):
    """Delete payment request"""
    payment_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    success = await db.delete_payment(payment_id, user_id)
    
    if success:
        await callback.message.edit_caption(
            caption=f"🗑 <b>Заявка #{payment_id} удалена</b>",
            parse_mode="HTML"
        )
        await callback.answer("✅ Заявка удалена")
    else:
        await callback.answer(
            "❌ Не удалось удалить заявку. Возможно, она уже оплачена.",
            show_alert=True
        )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Return to main menu"""
    await callback.message.delete()
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

