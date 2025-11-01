import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from database import Database
from models import Payment
from keyboards import (
    get_main_menu_keyboard,
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_payment_actions_keyboard,
    get_admin_payment_keyboard
)

# Создаем роутер для сотрудников
router = Router()
db = Database()
logger = logging.getLogger(__name__)


class PaymentStates(StatesGroup):
    """Состояния FSM для создания заявки"""
    waiting_for_screenshot = State()
    waiting_for_balance = State()
    waiting_for_username = State()
    confirming = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
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
    """Начало создания заявки"""
    user_id = message.from_user.id
    
    if not Config.is_employee(user_id):
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    await state.set_state(PaymentStates.waiting_for_screenshot)
    await message.answer(
        "📸 <b>Шаг 1/3: Скриншот</b>\n\n"
        "Отправьте скриншот (фото).\n\n"
        "Для отмены нажмите кнопку ниже.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )


@router.message(StateFilter(PaymentStates.waiting_for_screenshot), F.photo)
async def process_screenshot(message: Message, state: FSMContext):
    """Обработка скриншота"""
    # Сохраняем file_id самого большого фото
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
    """Обработка неверного формата скриншота"""
    await message.answer(
        "❌ Пожалуйста, отправьте фото (скриншот).\n\n"
        "Используйте функцию отправки фото в Telegram.",
        parse_mode="HTML"
    )


@router.message(StateFilter(PaymentStates.waiting_for_balance), F.text, ~F.text.in_(["❌ Отменить"]))
async def process_balance(message: Message, state: FSMContext):
    """Обработка баланса"""
    balance = message.text.strip()
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
    """Обработка юзернейма и показ превью"""
    username = message.text.strip()
    await state.update_data(username_field=username)
    
    # Получаем все данные
    data = await state.get_data()
    
    await state.set_state(PaymentStates.confirming)
    
    # Отправляем превью с фото
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


@router.callback_query(F.data == "confirm_payment", StateFilter(PaymentStates.confirming))
async def confirm_payment(callback: CallbackQuery, state: FSMContext, bot):
    """Подтверждение и создание заявки"""
    data = await state.get_data()
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    # Создаем заявку
    payment = Payment(
        employee_id=user_id,
        employee_username=username,
        balance=data['balance'],
        username_field=data['username_field'],
        screenshot_file_id=data['screenshot_file_id']
    )
    
    payment_id = await db.create_payment(payment)
    
    # Отправляем всем администраторам
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
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления администратору {admin_id}: {e}")
    
    await callback.message.edit_caption(
        caption=(
            f"✅ <b>Заявка #{payment_id} успешно создана!</b>\n\n"
            f"💰 <b>Баланс:</b> {data['balance']}\n"
            f"🔑 <b>Юзернейм:</b> {data['username_field']}\n\n"
            "Ожидайте обработки администратором."
        ),
        parse_mode="HTML"
    )
    
    await callback.answer("✅ Заявка отправлена!")
    await state.clear()
    
    # Возвращаем главное меню
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "cancel_payment", StateFilter(PaymentStates.confirming))
async def cancel_payment_confirm(callback: CallbackQuery, state: FSMContext):
    """Отмена создания заявки на этапе подтверждения"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "❌ Создание заявки отменено.",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.message(F.text == "❌ Отменить", StateFilter("*"))
async def cancel_operation(message: Message, state: FSMContext):
    """Отмена операции"""
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
    """Показ активных заявок пользователя"""
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
        await message.answer_photo(
            photo=payment.screenshot_file_id,
            caption=(
                f"📋 <b>Заявка #{payment.id}</b>\n"
                f"📅 <b>Создана:</b> {created_at}\n\n"
                f"💰 <b>Баланс:</b> {payment.balance}\n"
                f"🔑 <b>Юзернейм:</b> {payment.username_field}\n"
                f"📊 <b>Статус:</b> ⏳ Ожидает обработки"
            ),
            parse_mode="HTML",
            reply_markup=get_payment_actions_keyboard(payment.id)
        )


@router.callback_query(F.data.startswith("delete_"))
async def delete_payment(callback: CallbackQuery):
    """Удаление заявки"""
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
    """Возврат в главное меню"""
    await callback.message.delete()
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

