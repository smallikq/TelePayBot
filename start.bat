@echo off
chcp 65001 > nul
echo ========================================
echo    Telegram Payment Bot
echo ========================================
echo.

REM Проверка наличия .env файла
if not exist .env (
    echo ❌ Файл .env не найден!
    echo.
    echo Создайте файл .env на основе env_example.txt:
    echo    copy env_example.txt .env
    echo.
    echo Затем заполните его своими данными.
    echo.
    pause
    exit /b 1
)

echo ✅ Файл конфигурации найден
echo.
echo 🚀 Запуск бота...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ❌ Ошибка при запуске бота!
    echo.
    pause
)

