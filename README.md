# Telegram Payment Bot 💰

Telegram bot for managing employee payment requests with automatic notifications.

## 🎯 Features

- 📝 Create payment requests
- � Quick payment processing
- 📊 Automatic group notifications
- 📈 Payment statistics
- � Access control and validation

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
ADMIN_ID=your_telegram_id
GROUP_CHAT_ID=group_chat_id
EMPLOYEE_IDS=id1,id2,id3
```

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
    └── admin.py
```

## � Tech Stack

- aiogram 3.13.1
- aiosqlite
- python-dotenv

## 📝 License

MIT


