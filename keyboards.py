from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu for employees"""
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
    """Keyboard with cancel button"""
    keyboard = [[KeyboardButton(text="❌ Отменить")]]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Payment request confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_payment"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Administrator keyboard with payment buttons"""
    keyboard = [
        [
            InlineKeyboardButton(text="✍️ Отписал", callback_data=f"replied_{payment_id}")
        ],
        [
            InlineKeyboardButton(text="💵 Оплатить 15", callback_data=f"pay_15_{payment_id}"),
            InlineKeyboardButton(text="💵 Оплатить 25", callback_data=f"pay_25_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_actions_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Payment request actions keyboard for employee"""
    keyboard = [
        [
            InlineKeyboardButton(text="🗑 Удалить заявку", callback_data=f"delete_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with back button"""
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

