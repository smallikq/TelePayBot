# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Python

Make sure you have Python 3.9 or higher installed:

```bash
python --version
```

### Step 2: Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd TelePayBot

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure

```bash
# Copy example configuration
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Edit .env file with your favorite text editor
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

**Required values:**
- `BOT_TOKEN` - Get from @BotFather
- `ADMIN_ID` - Your Telegram ID from @userinfobot
- `GROUP_CHAT_ID` - Your group chat ID
- `EMPLOYEE_IDS` - Comma-separated employee IDs

### Step 4: Run

```bash
python main.py
```

You should see:
```
✅ Конфигурация загружена успешно
✅ База данных инициализирована
🤖 Бот запущен и готов к работе!
```

### Step 5: Test

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Try creating a payment request!

## 📱 First Payment Request

### As Employee:

1. Click "📝 Создать заявку"
2. Send a screenshot (any image)
3. Enter balance (e.g., "100$")
4. Enter username (e.g., "@myaccount")
5. Click "✅ Подтвердить"

### As Admin:

1. You'll receive notification with the request
2. Click "💵 Оплатить 15" or "💵 Оплатить 25"
3. Or click "💳 Другая сумма" for custom amount
4. Request will be posted to group chat automatically

## 🔧 Troubleshooting

### Bot doesn't respond

**Check:**
- Bot token is correct in `.env`
- Your ID is in EMPLOYEE_IDS or ADMIN_ID
- Bot is running (check console for errors)

### Can't find bot

**Solution:**
- Search by bot username in Telegram
- Make sure bot is not blocked

### Group chat posting fails

**Check:**
- Bot is added to group
- Bot has admin rights in group
- GROUP_CHAT_ID is correct (negative number with minus)

### Import errors

**Solution:**
```bash
pip install -r requirements.txt
```

## 📚 Next Steps

### For Admins:

- Try `/stats` to see statistics
- Try `/help` for command list
- Test custom payment amounts

### For Developers:

- Run tests: `pytest tests/ -v`
- Read `CONTRIBUTING.md` for development guidelines
- Check `IMPROVEMENTS.md` for feature details

## 🆘 Getting Help

### Common Questions

**Q: How to add more employees?**
A: Add their IDs to `EMPLOYEE_IDS` in `.env`, separated by commas

**Q: How to change payment amounts?**
A: Use "💳 Другая сумма" button or modify `keyboards.py`

**Q: Where is data stored?**
A: In `bot_database.db` SQLite file

**Q: How to backup data?**
A: Copy `bot_database.db` file regularly

### Still Need Help?

- Check `README.md` for detailed documentation
- Open an issue on GitHub
- Check bot logs in `bot.log` file

## ✅ Checklist

Before going to production:

- [ ] `.env` file is configured correctly
- [ ] Bot responds to `/start` command
- [ ] Admin receives payment requests
- [ ] Payments post to group chat
- [ ] Employee receives payment confirmation
- [ ] Database file is being created
- [ ] Logs are being written to `bot.log`
- [ ] `.env` is in `.gitignore` (security)

## 🎉 You're Ready!

Your TelePayBot is now configured and running. Enjoy!

---

**Need more details?** Check the full documentation in `README.md`
