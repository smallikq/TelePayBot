# Telegram Payment Bot 💰

Telegram bot for managing employee payment requests with automatic notifications.

## 🎯 Features

### For Employees:
- 📝 Create payment requests (screenshot + balance + username)
- 📋 View active requests
- 🗑 Delete unpaid requests
- ✅ Receive payment notifications

### For Administrator:
- 📨 Receive all requests from employees
- 💵 Quick payment buttons (15 or 25)
- 📊 Automatic status updates in database

### Automation:
- 📢 Automatic posting to group chat after payment
- 💾 Store all data in SQLite database
- 🎨 Beautiful interface with emojis and buttons

## 📋 Requirements

- Python 3.9+
- Telegram bot token (get from [@BotFather](https://t.me/BotFather))

## 🚀 Installation

### 1. Clone the repository
```bash
git clone <your-repo>
cd <project-folder>
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create configuration file

Create a `.env` file in the project root:

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

### 4. Configure `.env` file

Open `.env` and fill in the following parameters:

```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
GROUP_CHAT_ID=group_chat_id
EMPLOYEE_IDS=id1,id2,id3
```

#### How to get required data:

**BOT_TOKEN** - bot token:
1. Message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Follow the instructions
4. Copy the received token

**ADMIN_ID** and **EMPLOYEE_IDS** - Telegram user IDs:
1. Message [@userinfobot](https://t.me/userinfobot)
2. Send any message
3. Copy your ID

**GROUP_CHAT_ID** - group chat ID:
1. Create a group in Telegram
2. Add your bot to the group (make it an administrator)
3. Send any message to the group
4. Go to: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   (replace `<BOT_TOKEN>` with your bot token)
5. Find in the response `"chat":{"id":-1001234567890`
6. Copy this number (it starts with a minus sign)

## ▶️ Running

### Method 1: Via script (Windows)

```bash
start.bat
```

### Method 2: Direct

```bash
python main.py
```

The bot will start and send a notification to the administrator about the launch.

## 📱 Usage

### For Employees:

1. Start the bot with `/start` command
2. Press "📝 Создать заявку" (Create Request)
3. Send a screenshot (photo)
4. Enter balance
5. Enter username
6. Confirm the request

To view active requests, press "📋 Мои заявки" (My Requests)

### For Administrator:

1. Receive notification about new request
2. Check the data
3. Press "💵 Оплатить 15" (Pay 15) or "💵 Оплатить 25" (Pay 25)
4. Bot automatically sends information to group chat and notifies employee

### Workflow:

```
Employee                     Bot                    Administrator          Group Chat
    |                         |                           |                        |
    |---> Creates request --->|                           |                        |
    |    (screenshot+balance+username)                    |                        |
    |                         |                           |                        |
    |                         |---> Sends request ------->|                        |
    |                         |     with payment buttons  |                        |
    |                         |                           |                        |
    |                         |                           |<--- Clicks button      |
    |                         |                           |    "Pay 15/25"        |
    |                         |                           |                        |
    |                         |<--- Updates DB -----------|                        |
    |                         |                           |                        |
    |<--- Notification -------|                           |                        |
    |    "Paid!"              |                           |                        |
    |                         |                           |                        |
    |                         |---> Posts to chat ----------------------->|        |
    |                         |     (screenshot+data+amount)              |        |
```

## 🗂 Project Structure

```
.
├── main.py                 # Entry point, bot initialization
├── config.py              # Configuration and .env loading
├── database.py            # SQLite database operations
├── models.py              # Data models
├── keyboards.py           # Bot keyboards
├── handlers/              # Handlers
│   ├── __init__.py
│   ├── employee.py        # Employee functionality
│   └── admin.py           # Administrator functionality
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration example
├── .env                  # Your configuration (not in git)
├── .gitignore           # Ignored files
├── start.bat            # Windows startup script
└── README.md            # Documentation
```

## 🗄 Database

The bot uses SQLite database `bot_database.db` with the following structure:

**Table `payments`:**
- `id` - Request ID
- `employee_id` - Employee Telegram ID
- `employee_username` - Employee username
- `balance` - Balance from request
- `username_field` - Username from request
- `screenshot_file_id` - Screenshot ID in Telegram
- `status` - Status (pending/paid)
- `payment_amount` - Payment amount (15 or 25)
- `created_at` - Creation date
- `paid_at` - Payment date

## 🛠 Technologies

- **aiogram 3.13.1** - modern framework for Telegram bots
- **aiosqlite** - asynchronous SQLite operations
- **python-dotenv** - load configuration from .env

## 🔒 Security

- Access to functions is restricted by Telegram ID
- All IDs are stored in `.env` file (don't add it to git!)
- Employees can only delete their own unpaid requests
- Only administrator can process payments

## ❓ FAQ

**Q: How to add a new employee?**
A: Add their Telegram ID to `EMPLOYEE_IDS` in `.env` file separated by comma, then restart the bot.

**Q: Can I change payment amounts?**
A: Yes, modify values in `keyboards.py` file in `get_admin_payment_keyboard()` function.

**Q: How to view all payment history?**
A: All data is stored in `bot_database.db` file. You can open it with any SQLite client.

**Q: Bot doesn't send messages to group chat**
A: Make sure that:
1. Bot is added to the group
2. Bot has administrator rights in the group
3. GROUP_CHAT_ID is specified correctly (with minus sign at the beginning)

## 📝 License

MIT

## 👨‍💻 Support

If you encounter any problems, create an issue in the repository.

---

Made with ❤️ for payment management

