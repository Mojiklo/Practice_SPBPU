@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Check if the token has been properly set
findstr /C:"your_telegram_bot_token_here" "c:\python\.env" >nul
if %errorlevel% equ 0 (
    echo ERROR: You need to set your Telegram bot token in the .env file.
    echo Please edit the .env file and replace "8198536978:AAHvyWwR0pwMJObe3NvIpXpdGPZ1hAxU-44" with your actual token.
    echo You can get a token by talking to @BotFather on Telegram.
    pause
    exit /b 1
)

echo Starting the Telegram bot...
python main.py
pause