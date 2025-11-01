# Telegram Payment Bot 💰

Telegram bot for managing employee payment requests with automatic notifications.

## 🎯 Features

### For Employees

- 📝 Create payment requests (screenshot + balance + username)
- 📋 View active requests
- 🗑 Delete unpaid requests
- ✅ Receive payment notifications

### For Administrator

- 📨 Receive all requests from employees
- 💵 Quick payment buttons (15 or 25)
- � Custom payment amount support
- �📊 Automatic status updates in database
- 📈 View payment statistics

### Automation

- 📢 Automatic posting to group chat after payment
- 💾 Store all data in SQLite database
- 🎨 Beautiful interface with emojis and buttons
- 🔒 Input validation and rate limiting
- 📝 Comprehensive error logging

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

#### How to get required data

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

### For Employees

1. Start the bot with `/start` command
2. Press "📝 Создать заявку" (Create Request)
3. Send a screenshot (photo)
4. Enter balance
5. Enter username
6. Confirm the request

To view active requests, press "📋 Мои заявки" (My Requests)

### For Administrator

1. Receive notification about new request
2. Check the data
3. Press "✍️ Отписал" to mark as replied (optional)
4. Press "💵 Оплатить 15" (Pay 15), "💵 Оплатить 25" (Pay 25), or "💳 Другая сумма" (Custom Amount)
5. Bot automatically sends information to group chat and notifies employee

**Admin Commands:**

- `/stats` - View payment statistics for last 30 days
- `/help` - Show available commands

### Workflow

```text
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

```text
.
├── main.py                 # Entry point, bot initialization
├── config.py              # Configuration and .env loading
├── database.py            # SQLite database operations
├── models.py              # Data models
├── keyboards.py           # Bot keyboards
├── utils.py               # Utility functions and validators
├── handlers/              # Handlers
│   ├── __init__.py
│   ├── employee.py        # Employee functionality
│   └── admin.py           # Administrator functionality
├── tests/                 # Unit tests
│   └── test_bot.py        # Test cases
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
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
- `replied` - Whether admin replied to the request
- `employee_message_id` - Message ID in employee's chat
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
- Input validation to prevent malicious data
- HTML sanitization to prevent XSS attacks
- Rate limiting to prevent spam

## 🧪 Testing

Run tests with pytest:

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## ✨ New Features

### Input Validation

- Balance format validation
- Username format validation
- HTML sanitization for security

### Rate Limiting

- Prevents spam by limiting request creation frequency
- Configurable limits per user

### Statistics

- View payment statistics with `/stats` command
- See total payments, amounts, and per-employee breakdown

### Custom Payment Amounts

- Admin can enter any payment amount
- Not limited to just 15 or 25

### Enhanced Error Handling

- Comprehensive error logging to file and console
- Graceful error recovery
- Better error messages for users

### Graceful Shutdown

- Proper cleanup of database connections
- Clean bot session termination

## ❓ FAQ

**Q: How to add a new employee?**
A: Add their Telegram ID to `EMPLOYEE_IDS` in `.env` file separated by comma, then restart the bot.

**Q: Can I change payment amounts?**
A: Yes, you can use the "💳 Другая сумма" button to enter custom amounts, or modify default values in `keyboards.py`.

**Q: How to view all payment history?**
A: Use the `/stats` command for statistics, or open `bot_database.db` with any SQLite client for detailed history.

**Q: Bot doesn't send messages to group chat**
A: Make sure that:

1. Bot is added to the group
2. Bot has administrator rights in the group
3. GROUP_CHAT_ID is specified correctly (with minus sign at the beginning)

**Q: How do I run tests?**
A: Install dev dependencies with `pip install -r requirements-dev.txt` and run `pytest tests/`

## 📝 License

MIT

## 👨‍💻 Support

If you encounter any problems, create an issue in the repository.

---

Made with ❤️ for payment management


