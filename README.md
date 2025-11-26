# Telegram Payment Bot 💰

Telegram bot for managing employee payment requests with automatic notifications.

## 🎯 Features

- 📝 Create payment requests
- 💵 Quick payment processing
- 📊 Automatic group notifications
- 📈 Payment statistics
- 🔒 Access control and validation
- 👥 Employee management via bot (database-driven)

## 📋 Requirements

- Python 3.9+
- Telegram bot token from [@BotFather](https://t.me/BotFather)

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create `.env` file:

```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id,another_admin_id
GROUP_CHAT_ID=group_chat_id
```

**Note:** Employee IDs are now managed via database. See Migration section below.

### 3. Run

```bash
python main.py
```

## 📱 Usage

**Employees:**

- `/start` - Start bot
- Create requests with screenshot + balance + username
- View and manage active requests

**Admin:**

- Process payments with quick buttons (15/25) or custom amount
- Mark requests as replied
- View statistics with `/stats`
- Manage employees:
  - `/employees` - View all employees
  - `/add_employee` - Add new employee
  - `/remove_employee` - Remove employee
- `/help` - Show all admin commands

## 🗂 Project Structure

```text
├── main.py                # Bot entry point
├── config.py              # Configuration
├── database.py            # Database operations
├── models.py              # Data models
├── keyboards.py           # Bot keyboards
├── utils.py               # Validators and utilities
└── handlers/              # Request handlers
    ├── employee.py
    ├── admin.py
    └── employee_management.py
```

## � Tech Stack

- aiogram 3.13.1
- aiosqlite
- python-dotenv

## 🔄 Migration from .env to Database

If you're upgrading from a version that used `EMPLOYEE_IDS` in `.env`:

```bash
python migrate_employees.py
```

This will transfer all employee IDs from `.env` to the database. After migration, you can manage employees through bot commands.

## 📝 License

MIT


