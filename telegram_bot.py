import pyautogui
import keyboard
import os
import subprocess
import psutil
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

# ============= ТВОЙ ТОКЕН =============
TELEGRAM_TOKEN = "8748826626:AAG1v1LzQWoSvj5DUezHW2UDPLQxKhLnSIA"

# ============= ПРИЛОЖЕНИЯ И ИГРЫ =============
APPS = {
    "🎮 ИГРЫ": [
        {"name": "Steam", "cmd": "start steam://open", "icon": "🎮"},
        {"name": "CS:GO/CS2", "cmd": "start steam://rungameid/730", "icon": "🔫"},
        {"name": "Dota 2", "cmd": "start steam://rungameid/570", "icon": "⚔️"},
        {"name": "Minecraft", "cmd": "start minecraft://", "icon": "⛏️"},
        {"name": "Valorant", "cmd": "start riot://", "icon": "🎯"},
        {"name": "GTA V", "cmd": "start steam://rungameid/271590", "icon": "🚗"},
    ],
    "💬 ПРОГРАММЫ": [
        {"name": "Discord", "cmd": "start discord", "icon": "💬"},
        {"name": "Telegram", "cmd": "start telegram", "icon": "📱"},
        {"name": "Chrome", "cmd": "start chrome", "icon": "🌐"},
        {"name": "VS Code", "cmd": "start code", "icon": "📝"},
        {"name": "Spotify", "cmd": "start spotify", "icon": "🎵"},
        {"name": "Блокнот", "cmd": "notepad.exe", "icon": "📄"},
        {"name": "Калькулятор", "cmd": "calc.exe", "icon": "🧮"},
        {"name": "Проводник", "cmd": "explorer", "icon": "📁"},
    ],
    "🔧 СИСТЕМНЫЕ": [
        {"name": "Диспетчер задач", "cmd": "taskmgr", "icon": "⚙️"},
        {"name": "Командная строка", "cmd": "cmd", "icon": "💻"},
        {"name": "Панель управления", "cmd": "control", "icon": "🎛️"},
        {"name": "Блокировка", "cmd": "lock", "icon": "🔒"},
        {"name": "Спящий режим", "cmd": "sleep", "icon": "💤"},
        {"name": "Перезагрузка", "cmd": "restart", "icon": "🔄"},
        {"name": "Выключение", "cmd": "shutdown", "icon": "🔌"},
    ]
}

# ============= ЗАПУСК ПРИЛОЖЕНИЯ =============
def launch_app(cmd):
    try:
        if cmd == "lock":
            os.system('rundll32.exe user32.dll,LockWorkStation')
        elif cmd == "sleep":
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        elif cmd == "restart":
            os.system('shutdown /r /t 10')
        elif cmd == "shutdown":
            os.system('shutdown /s /t 30')
        elif cmd.startswith("start "):
            os.system(cmd)
        elif cmd.endswith(".exe"):
            os.startfile(cmd)
        else:
            subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

# ============= КОМАНДЫ БОТА =============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 ЗАПУСТИТЬ ИГРУ", callback_data='show_games')],
        [InlineKeyboardButton("💬 ЗАПУСТИТЬ ПРОГРАММУ", callback_data='show_apps')],
        [InlineKeyboardButton("🔧 СИСТЕМНЫЕ КОМАНДЫ", callback_data='show_system')],
        [InlineKeyboardButton("📸 СКРИНШОТ", callback_data='screenshot')],
        [InlineKeyboardButton("📊 СИСТЕМА", callback_data='stats')],
        [InlineKeyboardButton("❌ ОТМЕНА ВЫКЛЮЧЕНИЯ", callback_data='cancel')],
    ]
    await update.message.reply_text(
        "🤖 *PC REMOTE CONTROL*\n\n"
        "Управляй компьютером через Telegram!\n"
        "Выбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for game in APPS["🎮 ИГРЫ"]:
        keyboard.append([InlineKeyboardButton(f"{game['icon']} {game['name']}", callback_data=f"run_{game['cmd']}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data='back')])
    
    await update.callback_query.edit_message_text(
        "🎮 *ВЫБЕРИ ИГРУ:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for app in APPS["💬 ПРОГРАММЫ"]:
        keyboard.append([InlineKeyboardButton(f"{app['icon']} {app['name']}", callback_data=f"run_{app['cmd']}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data='back')])
    
    await update.callback_query.edit_message_text(
        "💬 *ВЫБЕРИ ПРОГРАММУ:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def show_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for tool in APPS["🔧 СИСТЕМНЫЕ"]:
        keyboard.append([InlineKeyboardButton(f"{tool['icon']} {tool['name']}", callback_data=f"run_{tool['cmd']}")])
    keyboard.append([InlineKeyboardButton("◀️ НАЗАД", callback_data='back')])
    
    await update.callback_query.edit_message_text(
        "🔧 *ВЫБЕРИ ДЕЙСТВИЕ:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 ЗАПУСТИТЬ ИГРУ", callback_data='show_games')],
        [InlineKeyboardButton("💬 ЗАПУСТИТЬ ПРОГРАММУ", callback_data='show_apps')],
        [InlineKeyboardButton("🔧 СИСТЕМНЫЕ КОМАНДЫ", callback_data='show_system')],
        [InlineKeyboardButton("📸 СКРИНШОТ", callback_data='screenshot')],
        [InlineKeyboardButton("📊 СИСТЕМА", callback_data='stats')],
        [InlineKeyboardButton("❌ ОТМЕНА ВЫКЛЮЧЕНИЯ", callback_data='cancel')],
    ]
    await update.callback_query.edit_message_text(
        "🤖 *PC REMOTE CONTROL*\n\nВыбери действие:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    
    # Навигация
    if action == 'back':
        await back_to_main(update, context)
        return
    elif action == 'show_games':
        await show_games(update, context)
        return
    elif action == 'show_apps':
        await show_apps(update, context)
        return
    elif action == 'show_system':
        await show_system(update, context)
        return
    
    # Запуск приложений
    if action.startswith('run_'):
        cmd = action[4:]
        if launch_app(cmd):
            await query.message.reply_text("✅ Запущено!")
        else:
            await query.message.reply_text("❌ Ошибка запуска")
        return
    
    # Команды
    if action == 'screenshot':
        screenshot = pyautogui.screenshot()
        img_io = io.BytesIO()
        screenshot.save(img_io, 'PNG')
        img_io.seek(0)
        await query.message.reply_photo(photo=img_io, caption="📸 Скриншот экрана")
    
    elif action == 'stats':
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        text = f"📊 *СИСТЕМА*\n\n"
        text += f"💻 CPU: {cpu}%\n"
        text += f"🧠 RAM: {ram.percent}% ({round(ram.used/1024**3,1)}GB/{round(ram.total/1024**3,1)}GB)\n"
        text += f"💾 Диск C: {disk.percent}% ({round(disk.free/1024**3,1)}GB свободно)"
        await query.message.reply_text(text, parse_mode='Markdown')
    
    elif action == 'cancel':
        os.system('shutdown /a')
        await query.message.reply_text("✅ Выключение отменено!")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    os.system('shutdown /a')
    await update.message.reply_text("✅ Выключение отменено!")

async def type_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if text:
        pyautogui.write(text)
        await update.message.reply_text(f"✍️ Напечатано: {text}")
    else:
        await update.message.reply_text("Используй: /type текст")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *КОМАНДЫ*\n\n"
        "/start - Главное меню\n"
        "/cancel - Отменить выключение\n"
        "/type текст - Напечатать текст на ПК\n"
        "/help - Справка",
        parse_mode='Markdown'
    )

# ============= ЗАПУСК =============
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🤖 TELEGRAM БОТ С ЗАПУСКОМ ПРИЛОЖЕНИЙ")
    print("="*50)
    print(f"✅ Токен: {TELEGRAM_TOKEN[:20]}...")
    print("📱 Напиши /start в Telegram боту")
    print("🎮 Добавь свои игры в словарь APPS")
    print("="*50 + "\n")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("type", type_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    app.run_polling()