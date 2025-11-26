import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import Config
from database import Database
from utils import format_user_link
from keyboards import get_employee_management_keyboard, get_cancel_keyboard, get_admin_menu_keyboard

router = Router()
db = Database()
logger = logging.getLogger(__name__)


class EmployeeStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_removal = State()


@router.message(F.text == "👥 Управление сотрудниками")
async def employee_management_menu(message: Message) -> None:
    """Показать меню управления сотрудниками"""
    user_id = message.from_user.id
    
    if not Config.is_admin(user_id):
        await message.answer("❌ У вас нет прав для этого действия!")
        return
    
    await message.answer(
        "👥 <b>Управление сотрудниками</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=get_employee_management_keyboard()
    )


@router.callback_query(F.data == "list_employees")
async def list_employees(callback: CallbackQuery) -> None:
    """Показать список всех сотрудников"""
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    try:
        employees = await db.get_all_employees()
        count = len(employees)
        
        if not employees:
            await callback.message.edit_text(
                "👥 <b>Список сотрудников пуст</b>\n\n"
                "Используйте кнопку '➕ Добавить сотрудника' для добавления.",
                parse_mode="HTML",
                reply_markup=get_employee_management_keyboard()
            )
            await callback.answer()
            return
        
        text = f"👥 <b>Список сотрудников ({count}):</b>\n\n"
        
        for emp in employees:
            user_link = format_user_link(emp['user_id'], emp['username'], emp['first_name'])
            added_date = emp['added_at'].strftime("%d.%m.%Y") if emp['added_at'] else "Неизвестно"
            text += f"• {user_link} (ID: {emp['user_id']})\n"
            text += f"  <i>Добавлен: {added_date}</i>\n\n"
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_employee_management_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error listing employees: {e}")
        await callback.answer("❌ Ошибка при получении списка сотрудников.", show_alert=True)


@router.callback_query(F.data == "add_employee")
async def add_employee_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать процесс добавления сотрудника"""
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    await state.set_state(EmployeeStates.waiting_for_user_id)
    await callback.message.answer(
        "👤 <b>Добавление сотрудника</b>\n\n"
        "Отправьте мне Telegram ID пользователя, которого хотите добавить в качестве сотрудника.\n\n"
        "💡 <b>Как получить ID:</b>\n"
        "1. Попросите пользователя написать боту @userinfobot\n"
        "2. Бот покажет его ID\n"
        "3. Отправьте этот ID сюда\n\n"
        "Или перешлите мне сообщение от этого пользователя.\n\n"
        "Для отмены нажмите кнопку ниже.",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(EmployeeStates.waiting_for_user_id, F.text)
async def add_employee_process(message: Message, state: FSMContext) -> None:
    """Обработать добавление сотрудника"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Добавление сотрудника отменено.")
        return
    
    # Проверяем, является ли это переадресованным сообщением
    if message.forward_from:
        target_user_id = message.forward_from.id
        username = message.forward_from.username
        first_name = message.forward_from.first_name
    else:
        # Пытаемся извлечь ID из текста
        try:
            target_user_id = int(message.text.strip())
            username = None
            first_name = None
        except ValueError:
            await message.answer(
                "❌ Неверный формат ID. Отправьте числовой ID пользователя или перешлите его сообщение.\n\n"
                "Для отмены отправьте /cancel",
                parse_mode="HTML"
            )
            return
    
    # Проверяем, не является ли пользователь уже сотрудником
    is_already_employee = await db.is_employee(target_user_id)
    if is_already_employee:
        await message.answer(
            f"⚠️ Пользователь с ID {target_user_id} уже является сотрудником!",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    # Добавляем сотрудника
    success = await db.add_employee(
        user_id=target_user_id,
        username=username,
        first_name=first_name,
        added_by=message.from_user.id
    )
    
    if success:
        user_link = format_user_link(target_user_id, username, first_name)
        await message.answer(
            f"✅ <b>Сотрудник успешно добавлен!</b>\n\n"
            f"👤 {user_link}\n"
            f"🆔 ID: {target_user_id}\n\n"
            f"Теперь этот пользователь может создавать заявки на оплату.",
            parse_mode="HTML",
            reply_markup=get_admin_menu_keyboard()
        )
        
        # Уведомляем нового сотрудника (если возможно)
        try:
            from main import bot_instance
            if bot_instance:
                await bot_instance.send_message(
                    target_user_id,
                    "🎉 <b>Поздравляем!</b>\n\n"
                    "Вы были добавлены в качестве сотрудника.\n"
                    "Теперь вы можете создавать заявки на оплату.\n\n"
                    "Используйте команду /start для начала работы.",
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.warning(f"Could not notify new employee {target_user_id}: {e}")
    else:
        await message.answer(
            "❌ Не удалось добавить сотрудника. Попробуйте позже.",
            parse_mode="HTML",
            reply_markup=get_admin_menu_keyboard()
        )
    
    await state.clear()


@router.callback_query(F.data == "remove_employee")
async def remove_employee_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Начать процесс удаления сотрудника"""
    user_id = callback.from_user.id
    
    if not Config.is_admin(user_id):
        await callback.answer("❌ У вас нет прав для этого действия!", show_alert=True)
        return
    
    employees = await db.get_all_employees()
    
    if not employees:
        await callback.answer("Нечего удалять - список пуст", show_alert=True)
        return
    
    text = "👥 <b>Выберите сотрудника для удаления:</b>\n\n"
    
    for emp in employees:
        user_link = format_user_link(emp['user_id'], emp['username'], emp['first_name'])
        text += f"• {user_link} - ID: <code>{emp['user_id']}</code>\n"
    
    text += "\nОтправьте ID сотрудника, которого хотите удалить.\n\n"
    text += "Для отмены нажмите кнопку ниже."
    
    await state.set_state(EmployeeStates.waiting_for_removal)
    await callback.message.answer(text, parse_mode="HTML", reply_markup=get_cancel_keyboard())
    await callback.answer()


@router.message(EmployeeStates.waiting_for_removal, F.text)
async def remove_employee_process(message: Message, state: FSMContext) -> None:
    """Обработать удаление сотрудника"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer("❌ Удаление сотрудника отменено.")
        return
    
    try:
        target_user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ Неверный формат ID. Отправьте числовой ID пользователя.\n\n"
            "Для отмены отправьте /cancel",
            parse_mode="HTML"
        )
        return
    
    # Проверяем, является ли пользователь сотрудником
    is_employee = await db.is_employee(target_user_id)
    if not is_employee:
        await message.answer(
            f"⚠️ Пользователь с ID {target_user_id} не является сотрудником!",
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    # Удаляем сотрудника
    success = await db.remove_employee(target_user_id)
    
    if success:
        await message.answer(
            f"✅ <b>Сотрудник успешно удален!</b>\n\n"
            f"🆔 ID: {target_user_id}\n\n"
            f"Пользователь больше не сможет создавать заявки на оплату.",
            parse_mode="HTML",
            reply_markup=get_admin_menu_keyboard()
        )
        
        # Уведомляем бывшего сотрудника (если возможно)
        try:
            from main import bot_instance
            if bot_instance:
                await bot_instance.send_message(
                    target_user_id,
                    "ℹ️ <b>Уведомление</b>\n\n"
                    "Ваш доступ к созданию заявок на оплату был отозван.\n"
                    "Если у вас есть вопросы, обратитесь к администратору.",
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.warning(f"Could not notify removed employee {target_user_id}: {e}")
    else:
        await message.answer(
            "❌ Не удалось удалить сотрудника. Попробуйте позже.",
            parse_mode="HTML",
            reply_markup=get_admin_menu_keyboard()
        )
    
    await state.clear()


@router.message(F.text == "❌ Отменить", EmployeeStates)
async def cancel_employee_operation(message: Message, state: FSMContext) -> None:
    """Отменить текущую операцию"""
    await state.clear()
    await message.answer(
        "❌ Операция отменена.",
        reply_markup=get_admin_menu_keyboard()
    )
