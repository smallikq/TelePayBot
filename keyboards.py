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


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню для администраторов"""
    keyboard = [
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="❓ Помощь")],
        [KeyboardButton(text="👥 Управление сотрудниками")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )


def get_employee_management_keyboard() -> InlineKeyboardMarkup:
    """Меню управления сотрудниками"""
    keyboard = [
        [InlineKeyboardButton(text="📋 Список сотрудников", callback_data="list_employees")],
        [InlineKeyboardButton(text="➕ Добавить сотрудника", callback_data="add_employee")],
        [InlineKeyboardButton(text="➖ Удалить сотрудника", callback_data="remove_employee")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка отмены"""
    keyboard = [[KeyboardButton(text="❌ Отменить")]]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """Кнопки подтверждения заявки"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_payment"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_payment_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Кнопки действий администратора для заявки"""
    keyboard = [
        [
            InlineKeyboardButton(text="✍️ Отписал", callback_data=f"replied_{payment_id}")
        ],
        [
            InlineKeyboardButton(text="💵 Оплатить 15", callback_data=f"pay_15_{payment_id}"),
            InlineKeyboardButton(text="💵 Оплатить 25", callback_data=f"pay_25_{payment_id}")
        ],
        [
            InlineKeyboardButton(text="💳 Другая сумма", callback_data=f"custom_pay_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_payment_actions_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    """Кнопки действий сотрудника для заявки"""
    keyboard = [
        [
            InlineKeyboardButton(text="🗑 Удалить заявку", callback_data=f"delete_{payment_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад"""
    keyboard = [
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

