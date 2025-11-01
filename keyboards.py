from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню для сотрудников"""
    keyboard = [
        [KeyboardButton(text="📝 Создать заявку")],
        [KeyboardButton(text="📋 Мои заявки")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = [[KeyboardButton(text="❌ Отменить")]]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подтверждения заявки"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_payment"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для администратора с кнопками оплаты"""
    keyboard = [
        [
            InlineKeyboardButton(text="💵 Оплатить 15", callback_data=f"pay_15_{payment_id}"),
            InlineKeyboardButton(text="💵 Оплатить 25", callback_data=f"pay_25_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_actions_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с заявкой для сотрудника"""
    keyboard = [
        [
            InlineKeyboardButton(text="🗑 Удалить заявку", callback_data=f"delete_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

