"""
╔══════════════════════════════════════════════════════════════════╗
║     PC REMOTE CONTROL PRO v7.0 - С TELEGRAM БОТОМ                ║
║     🔥 ПОЛНОЕ УПРАВЛЕНИЕ ПК С ТЕЛЕФОНА И TELEGRAM               ║
║     📊 РЕАЛЬНАЯ ТЕМПЕРАТУРА ПРОЦЕССОРА                          ║
║     🤖 УПРАВЛЕНИЕ ЧЕРЕЗ TELEGRAM БОТА                           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import pyautogui
import keyboard
import os
import subprocess
import socket
import time
import threading
import requests
import json
import io
import psutil
import platform
import datetime
import ctypes
import sys
from flask import Flask, request, jsonify, render_template_string, send_file
from PIL import Image

# ============= TELEGRAM БОТ =============
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

# ============= НАСТРОЙКИ =============
PASSWORD = "1234"
SCREEN_QUALITY = 70
VERSION = "7.0.0"
APP_NAME = "PC Remote Control Pro"

# ТВОЙ ТОКЕН TELEGRAM БОТА (ВСТАВЬ СВОЙ)
TELEGRAM_TOKEN = "8748826626:AAG1v1LzQWoSvj5DUezHW2UDPLQxKhLnSIA"

# Расширенные быстрые команды
QUICK_COMMANDS = {
    "🎮 ИГРЫ": [
        {"name": "Steam", "cmd": "start steam://open", "icon": "🎮"},
        {"name": "Epic Games", "cmd": "start com.epicgames.launcher://", "icon": "🎯"},
        {"name": "CS:GO/CS2", "cmd": "start steam://rungameid/730", "icon": "🔫"},
        {"name": "Dota 2", "cmd": "start steam://rungameid/570", "icon": "⚔️"},
        {"name": "Valorant", "cmd": "start riot://", "icon": "🎯"},
        {"name": "Minecraft", "cmd": "start minecraft://", "icon": "⛏️"},
        {"name": "GTA V", "cmd": "start steam://rungameid/271590", "icon": "🚗"},
        {"name": "Cyberpunk", "cmd": "start steam://rungameid/1091500", "icon": "🤖"}
    ],
    "💬 ПРОГРАММЫ": [
        {"name": "Discord", "cmd": "start discord", "icon": "💬"},
        {"name": "Telegram", "cmd": "start telegram", "icon": "📱"},
        {"name": "Chrome", "cmd": "start chrome", "icon": "🌐"},
        {"name": "VSCode", "cmd": "start code", "icon": "📝"},
        {"name": "Spotify", "cmd": "start spotify", "icon": "🎵"},
        {"name": "Photoshop", "cmd": "start photoshop", "icon": "🎨"},
        {"name": "Блокнот", "cmd": "notepad.exe", "icon": "📄"},
        {"name": "Калькулятор", "cmd": "calc.exe", "icon": "🧮"}
    ],
    "🔧 СИСТЕМА": [
        {"name": "Диспетчер задач", "cmd": "taskmgr", "icon": "⚙️"},
        {"name": "Блокировка", "cmd": "lock", "icon": "🔒"},
        {"name": "Спящий режим", "cmd": "sleep", "icon": "💤"},
        {"name": "Перезагрузка", "cmd": "restart", "icon": "🔄"},
        {"name": "Очистка DNS", "cmd": "ipconfig /flushdns", "icon": "🧹"},
        {"name": "Панель управления", "cmd": "control", "icon": "🎛️"},
        {"name": "Командная строка", "cmd": "cmd", "icon": "💻"},
        {"name": "Проводник", "cmd": "explorer", "icon": "📁"}
    ]
}

# ============= ФУНКЦИЯ ПОЛУЧЕНИЯ ТЕМПЕРАТУРЫ =============
def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for sensor_name in ['coretemp', 'k10temp', 'cpu-thermal', 'acpitz', 'cpu', 'CPUTIN', 'CPU']:
                if sensor_name in temps and temps[sensor_name]:
                    temp = temps[sensor_name][0].current
                    if temp and temp > 0 and temp < 120:
                        return round(temp, 1)
    except:
        pass
    
    try:
        import wmi
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        for sensor in w.Sensor():
            if sensor.SensorType == 'Temperature' and ('CPU' in str(sensor.Name) or 'Core' in str(sensor.Name)):
                if sensor.Value and sensor.Value > 0 and sensor.Value < 120:
                    return round(sensor.Value, 1)
    except:
        pass
    
    return "N/A"

# ============= TELEGRAM БОТ КОМАНДЫ =============
async def tg_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 Скриншот", callback_data='screenshot')],
        [InlineKeyboardButton("🎮 Запустить игру", callback_data='show_games'),
         InlineKeyboardButton("💬 Запустить программу", callback_data='show_apps')],
        [InlineKeyboardButton("🔒 Блокировка", callback_data='lock'),
         InlineKeyboardButton("💤 Сон", callback_data='sleep')],
        [InlineKeyboardButton("🔄 Перезагрузка", callback_data='restart'),
         InlineKeyboardButton("🔌 Выключение", callback_data='shutdown')],
        [InlineKeyboardButton("🔊 Громкость +", callback_data='vol_up'),
         InlineKeyboardButton("🔉 Громкость -", callback_data='vol_down'),
         InlineKeyboardButton("🔇 Mute", callback_data='vol_mute')],
        [InlineKeyboardButton("📊 Система", callback_data='stats'),
         InlineKeyboardButton("⌨️ Ввести текст", callback_data='type_text')],
        [InlineKeyboardButton("❌ Отменить выключение", callback_data='cancel')],
    ]
    await update.message.reply_text(
        "🤖 *PC Remote Control*\n\nУправляй компьютером из Telegram!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def tg_show_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for game in QUICK_COMMANDS["🎮 ИГРЫ"]:
        keyboard.append([InlineKeyboardButton(f"{game['icon']} {game['name']}", callback_data=f"run_{game['cmd']}")])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')])
    await update.callback_query.edit_message_text(
        "🎮 *Выбери игру:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def tg_show_apps_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for app in QUICK_COMMANDS["💬 ПРОГРАММЫ"]:
        keyboard.append([InlineKeyboardButton(f"{app['icon']} {app['name']}", callback_data=f"run_{app['cmd']}")])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data='back_to_main')])
    await update.callback_query.edit_message_text(
        "💬 *Выбери программу:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def tg_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == 'back_to_main':
        await tg_start(update, context)
        return
    elif action == 'show_games':
        await tg_show_games_menu(update, context)
        return
    elif action == 'show_apps':
        await tg_show_apps_menu(update, context)
        return
    elif action == 'type_text':
        await query.message.reply_text("💬 Введи текст для печати:")
        context.user_data['awaiting_text'] = True
        return
    
    if action.startswith('run_'):
        cmd = action[4:]
        try:
            if cmd.startswith("start "):
                os.system(cmd)
            elif cmd.endswith(".exe"):
                os.startfile(cmd)
            else:
                subprocess.Popen(cmd, shell=True)
            await query.message.reply_text("✅ Запущено!")
        except:
            await query.message.reply_text("❌ Ошибка запуска")
        return
    
    if action == 'screenshot':
        screenshot = pyautogui.screenshot()
        img_io = io.BytesIO()
        screenshot.save(img_io, 'PNG')
        img_io.seek(0)
        await query.message.reply_photo(photo=img_io, caption="📸 Скриншот")
    elif action == 'lock':
        os.system('rundll32.exe user32.dll,LockWorkStation')
        await query.message.reply_text("🔒 Компьютер заблокирован")
    elif action == 'sleep':
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        await query.message.reply_text("💤 Спящий режим")
    elif action == 'restart':
        os.system('shutdown /r /t 10')
        await query.message.reply_text("🔄 Перезагрузка через 10 сек!")
    elif action == 'shutdown':
        os.system('shutdown /s /t 30')
        await query.message.reply_text("🔌 Выключение через 30 сек!")
    elif action == 'cancel':
        os.system('shutdown /a')
        await query.message.reply_text("✅ Отменено!")
    elif action == 'vol_up':
        keyboard.press_and_release('volume up')
        await query.message.reply_text("🔊 Громкость +")
    elif action == 'vol_down':
        keyboard.press_and_release('volume down')
        await query.message.reply_text("🔉 Громкость -")
    elif action == 'vol_mute':
        keyboard.press_and_release('volume mute')
        await query.message.reply_text("🔇 Mute")
    elif action == 'stats':
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        temp = get_cpu_temperature()
        text = f"📊 *Система*\n\n💻 CPU: {cpu}%\n🧠 RAM: {ram.percent}%\n💾 Диск C: {disk.percent}%\n🌡️ Температура: {temp}°C"
        await query.message.reply_text(text, parse_mode='Markdown')

async def tg_handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_text'):
        text = update.message.text
        context.user_data['awaiting_text'] = False
        pyautogui.write(text)
        await update.message.reply_text(f"✍️ Напечатано: {text}")
    else:
        await update.message.reply_text("Используй /start")

async def tg_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    os.system('shutdown /a')
    await update.message.reply_text("✅ Отменено!")

# ============= HTML ИНТЕРФЕЙС =============
HTML = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#1a1a2e">
    <title>PC Remote Control Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; min-height: 100vh; padding: 20px; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes glow { 0% { box-shadow: 0 0 5px rgba(0,210,211,0.5); } 100% { box-shadow: 0 0 20px rgba(0,210,211,0.8); } }
        .container { max-width: 550px; margin: 0 auto; animation: fadeInUp 0.6s ease-out; }
        .status-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 24px; padding: 16px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.1); }
        .status-card.connected { background: linear-gradient(135deg, rgba(0,210,211,0.2), rgba(0,180,190,0.1)); border-color: rgba(0,210,211,0.5); }
        .status-led { width: 12px; height: 12px; border-radius: 50%; background: #ff4757; display: inline-block; margin-right: 8px; box-shadow: 0 0 5px #ff4757; }
        .status-led.connected { background: #00d2d3; box-shadow: 0 0 10px #00d2d3; animation: glow 1s infinite alternate; }
        .status-text { font-weight: 600; font-size: 14px; }
        .ip-badge { background: rgba(0,0,0,0.3); padding: 6px 12px; border-radius: 20px; font-size: 11px; font-family: monospace; }
        .auth-card, .card { background: rgba(255,255,255,0.08); backdrop-filter: blur(10px); border-radius: 24px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; font-size: 12px; color: rgba(255,255,255,0.6); margin-bottom: 8px; }
        .input-group input { width: 100%; padding: 14px 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: white; font-size: 14px; transition: all 0.3s ease; }
        .input-group input:focus { outline: none; border-color: #00d2d3; box-shadow: 0 0 15px rgba(0,210,211,0.3); }
        .btn-primary { width: 100%; padding: 14px; border-radius: 16px; border: none; background: linear-gradient(135deg, #00d2d3, #00b894); color: #1a1a2e; font-weight: 700; font-size: 16px; cursor: pointer; transition: all 0.3s ease; }
        .btn-primary:active { transform: scale(0.98); }
        .tabs { display: flex; gap: 8px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px; scrollbar-width: none; }
        .tabs::-webkit-scrollbar { display: none; }
        .tab { flex-shrink: 0; padding: 12px 18px; background: rgba(255,255,255,0.08); border-radius: 40px; font-size: 13px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; white-space: nowrap; }
        .tab i { margin-right: 8px; }
        .tab.active { background: linear-gradient(135deg, #e94560, #ff6b6b); box-shadow: 0 5px 20px rgba(233,69,96,0.3); }
        .panel { display: none; animation: fadeInUp 0.4s ease-out; }
        .panel.active { display: block; }
        .card-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
        .card-title i { color: #00d2d3; font-size: 20px; }
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
        .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
        .btn { padding: 14px 8px; border-radius: 16px; border: none; font-weight: 600; font-size: 13px; cursor: pointer; transition: all 0.2s ease; text-align: center; }
        .btn:active { transform: scale(0.95); }
        .btn-icon { background: linear-gradient(135deg, #e94560, #ff6b6b); color: white; }
        .btn-secondary { background: rgba(255,255,255,0.12); color: white; }
        .btn-danger { background: linear-gradient(135deg, #ff4757, #ff6b81); color: white; }
        .btn-success { background: linear-gradient(135deg, #00d2d3, #00b894); color: #1a1a2e; }
        .joystick-container { display: flex; justify-content: center; margin-bottom: 20px; }
        .joystick { width: 200px; height: 200px; background: rgba(0,0,0,0.4); border-radius: 50%; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border: 2px solid rgba(255,255,255,0.1); }
        .joystick-handle { width: 70px; height: 70px; background: linear-gradient(135deg, #e94560, #ff6b6b); border-radius: 50%; position: absolute; top: 65px; left: 65px; cursor: pointer; box-shadow: 0 5px 20px rgba(233,69,96,0.4); transition: transform 0.02s linear; }
        .screen-container { background: #000; border-radius: 20px; padding: 10px; margin-bottom: 15px; }
        .screen-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 12px; color: rgba(255,255,255,0.6); }
        .screen-img { width: 100%; border-radius: 12px; cursor: crosshair; transition: opacity 0.2s; }
        .screen-img.loading { opacity: 0.5; }
        .screen-controls { display: flex; gap: 10px; margin-top: 10px; }
        .chat-container { background: rgba(0,0,0,0.3); border-radius: 16px; height: 300px; overflow-y: auto; padding: 15px; margin-bottom: 15px; }
        .message { margin-bottom: 12px; display: flex; gap: 10px; }
        .message.user { justify-content: flex-end; }
        .message-bubble { max-width: 80%; padding: 10px 14px; border-radius: 18px; font-size: 13px; }
        .message.user .message-bubble { background: linear-gradient(135deg, #e94560, #ff6b6b); border-radius: 18px 4px 18px 18px; }
        .message.ai .message-bubble { background: rgba(255,255,255,0.1); border-radius: 4px 18px 18px 18px; }
        .metric { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .metric-value { font-weight: 700; color: #00d2d3; }
        .spinner { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.2); border-top-color: #00d2d3; border-radius: 50%; animation: spin 1s linear infinite; margin: 20px auto; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
        .toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.9); backdrop-filter: blur(10px); padding: 12px 20px; border-radius: 40px; font-size: 13px; z-index: 1000; animation: fadeInUp 0.3s ease; }
        .temp-high { color: #ff6b6b; }
        .temp-mid { color: #ffa502; }
        .temp-low { color: #00d2d3; }
        @media (max-width: 450px) { body { padding: 12px; } .grid-5 { grid-template-columns: repeat(4, 1fr); } .btn { padding: 12px 6px; font-size: 12px; } }
    </style>
</head>
<body>
<div class="container">
    <div class="status-card" id="statusCard">
        <div><span class="status-led" id="statusLed"></span><span class="status-text" id="statusText">Не подключено</span></div>
        <div class="ip-badge" id="ipBadge">📍 ---</div>
    </div>
    <div class="auth-card" id="authCard">
        <div class="input-group"><label><i class="fas fa-lock"></i> Пароль доступа</label><input type="password" id="password" placeholder="Введите пароль" value="1234"></div>
        <div class="input-group"><label><i class="fas fa-network-wired"></i> IP адрес ПК</label><input type="text" id="pcIp" placeholder="Оставьте пустым для автоопределения"></div>
        <button class="btn-primary" onclick="connect()"><i class="fas fa-plug"></i> Подключиться</button>
    </div>
    <div class="card" id="publicUrlCard" style="display:none; background: linear-gradient(135deg, #00b89420, #00d2d320);">
        <div class="card-title"><i class="fas fa-globe"></i> Публичный доступ</div>
        <div id="publicUrl" style="font-size: 12px; word-break: break-all; font-family: monospace;"></div>
    </div>
    <div class="tabs" id="tabs" style="display:none;">
        <div class="tab active" onclick="switchTab('screen')"><i class="fas fa-desktop"></i> Экран</div>
        <div class="tab" onclick="switchTab('mouse')"><i class="fas fa-mouse-pointer"></i> Мышь</div>
        <div class="tab" onclick="switchTab('keyboard')"><i class="fas fa-keyboard"></i> Клава</div>
        <div class="tab" onclick="switchTab('macros')"><i class="fas fa-bolt"></i> Макросы</div>
        <div class="tab" onclick="switchTab('apps')"><i class="fas fa-apps"></i> Приложения</div>
        <div class="tab" onclick="switchTab('system')"><i class="fas fa-chart-line"></i> Система</div>
        <div class="tab" onclick="switchTab('ai')"><i class="fas fa-robot"></i> AI</div>
        <div class="tab" onclick="switchTab('settings')"><i class="fas fa-cog"></i> Настройки</div>
    </div>
    <div id="panel-screen" class="panel active">
        <div class="card"><div class="card-title"><i class="fas fa-desktop"></i> Монитор ПК</div>
        <div class="screen-container"><div class="screen-header"><span><i class="fas fa-chart-line"></i> <span id="cursorPos">курсор: --,--</span></span><span id="refreshTime">--:--:--</span></div>
        <img id="screenImg" class="screen-img" alt="Screen" onclick="handleScreenClick(event)" style="cursor: crosshair;">
        <div class="screen-controls"><button class="btn btn-secondary" onclick="refreshScreen()"><i class="fas fa-sync-alt"></i> Обновить</button><button class="btn btn-secondary" onclick="toggleAutoRefresh()" id="autoRefreshBtn"><i class="fas fa-pause"></i> Пауза</button><button class="btn btn-secondary" onclick="setQuality('low')"><i class="fas fa-mobile-alt"></i> Низкое</button><button class="btn btn-secondary" onclick="setQuality('high')"><i class="fas fa-desktop"></i> Высокое</button></div></div></div>
    </div>
    <div id="panel-mouse" class="panel">
        <div class="card"><div class="card-title"><i class="fas fa-mouse-pointer"></i> Управление мышью</div>
        <div class="joystick-container"><div class="joystick" id="joystickArea"><div class="joystick-handle" id="joystickHandle"></div></div></div>
        <div class="grid-3"><button class="btn btn-icon" onclick="sendClick('left')"><i class="fas fa-mouse"></i> ЛКМ</button><button class="btn btn-icon" onclick="sendClick('right')"><i class="fas fa-mouse"></i> ПКМ</button><button class="btn btn-icon" onclick="sendClick('middle')"><i class="fas fa-mouse"></i> СКМ</button><button class="btn btn-secondary" onclick="sendScroll(100)"><i class="fas fa-arrow-up"></i> Вверх</button><button class="btn btn-secondary" onclick="sendScroll(-100)"><i class="fas fa-arrow-down"></i> Вниз</button><button class="btn btn-secondary" onclick="getPos()"><i class="fas fa-location-dot"></i> Позиция</button></div>
        <div id="mouseCoords" style="text-align:center; margin-top:15px; font-size:12px; color:#00d2d3;">X: --, Y: --</div></div>
    </div>
    <div id="panel-keyboard" class="panel">
        <div class="card"><div class="card-title"><i class="fas fa-keyboard"></i> Клавиатура</div>
        <div class="grid-5"><button class="btn btn-secondary" onclick="sendKey('win')"><i class="fab fa-windows"></i></button><button class="btn btn-secondary" onclick="sendKey('alt')">Alt</button><button class="btn btn-secondary" onclick="sendKey('ctrl')">Ctrl</button><button class="btn btn-secondary" onclick="sendKey('shift')">Shift</button><button class="btn btn-secondary" onclick="sendKey('tab')">Tab</button><button class="btn btn-secondary" onclick="sendKey('space')">Пробел</button><button class="btn btn-secondary" onclick="sendKey('enter')">Enter</button><button class="btn btn-secondary" onclick="sendKey('backspace')">⌫</button><button class="btn btn-secondary" onclick="sendKey('delete')">Del</button><button class="btn btn-secondary" onclick="sendKey('esc')">Esc</button><button class="btn btn-secondary" onclick="sendKey('up')"><i class="fas fa-arrow-up"></i></button><button class="btn btn-secondary" onclick="sendKey('left')"><i class="fas fa-arrow-left"></i></button><button class="btn btn-secondary" onclick="sendKey('down')"><i class="fas fa-arrow-down"></i></button><button class="btn btn-secondary" onclick="sendKey('right')"><i class="fas fa-arrow-right"></i></button><button class="btn btn-secondary" onclick="sendKey('f5')">F5</button></div>
        <input type="text" class="input-group" id="textToType" placeholder="Введите текст для печати..." style="margin-top:15px;"><button class="btn btn-success" onclick="sendType()" style="margin-top:10px;"><i class="fas fa-print"></i> Напечатать</button></div>
    </div>
    <div id="panel-macros" class="panel"><div class="card"><div class="card-title"><i class="fas fa-bolt"></i> Быстрые команды</div><div id="macrosContainer"></div></div></div>
    <div id="panel-apps" class="panel">
        <div class="card"><div class="card-title"><i class="fas fa-apps"></i> Управление громкостью</div><div id="appVolumesContainer"><div class="spinner"></div></div><button class="btn btn-secondary" onclick="refreshAppVolumes()" style="margin-top:15px;"><i class="fas fa-sync-alt"></i> Обновить список</button></div>
        <div class="card"><div class="card-title"><i class="fas fa-microphone"></i> Голосовые команды</div><button class="btn btn-primary" onclick="startVoice()"><i class="fas fa-microphone"></i> Начать распознавание</button><div id="voiceResult" style="margin-top:15px; padding:12px; background:rgba(0,0,0,0.3); border-radius:16px; font-size:12px;"></div></div>
    </div>
    <div id="panel-system" class="panel">
        <div class="card"><div class="card-title"><i class="fas fa-chart-line"></i> Мониторинг системы</div><div id="systemMetrics"></div></div>
        <div class="card"><div class="card-title"><i class="fas fa-power-off"></i> Управление питанием</div>
        <div class="grid-3"><button class="btn btn-danger" onclick="shutdown(30)"><i class="fas fa-power-off"></i> Выкл (30с)</button><button class="btn btn-secondary" onclick="cancelShutdown()"><i class="fas fa-ban"></i> Отмена</button><button class="btn btn-secondary" onclick="lockPC()"><i class="fas fa-lock"></i> Блокировка</button><button class="btn btn-secondary" onclick="restartPC()"><i class="fas fa-sync-alt"></i> Перезагрузка</button><button class="btn btn-secondary" onclick="sleepPC()"><i class="fas fa-moon"></i> Сон</button><button class="btn btn-secondary" onclick="sendNotification()"><i class="fas fa-bell"></i> Тест уведомления</button></div></div>
    </div>
    <div id="panel-ai" class="panel">
        <div class="card"><div class="card-title"><i class="fas fa-robot"></i> DeepSeek AI Помощник</div>
        <div class="chat-container" id="chatMessages"><div class="message ai"><div class="message-bubble">👋 Привет! Я DeepSeek AI. Могу помочь с управлением ПК, ответить на вопросы или просто поболтать. Что желаешь?</div></div></div>
        <div class="input-group"><input type="text" id="aiInput" placeholder="Спроси у ИИ..." onkeypress="if(event.key==='Enter') askAI()"></div>
        <div class="grid-2"><button class="btn btn-primary" onclick="askAI()"><i class="fas fa-paper-plane"></i> Отправить</button><button class="btn btn-secondary" onclick="voiceAI()"><i class="fas fa-microphone"></i> Голос</button></div></div>
    </div>
    <div id="panel-settings" class="panel">
        <div class="card"><div class="card-title"><i class="fas fa-cog"></i> Настройки</div>
        <div class="metric"><span>Версия приложения</span><span class="metric-value">v7.0.0</span></div>
        <div class="metric"><span>Статус сервера</span><span class="metric-value" id="serverStatus">● Активен</span></div>
        <div class="metric"><span>Качество экрана</span><span class="metric-value" id="qualitySetting">Среднее</span></div>
        <button class="btn btn-secondary" onclick="changePassword()" style="margin-top:15px;"><i class="fas fa-key"></i> Сменить пароль</button>
        <button class="btn btn-danger" onclick="disconnect()" style="margin-top:10px;"><i class="fas fa-sign-out-alt"></i> Отключиться</button></div>
    </div>
</div>
<script>
    let pcUrl = '', connected = false, password = '1234', autoRefresh = true, refreshTimer = null, currentQuality = 'medium';
    let screenWidth = 1920, screenHeight = 1080, moveInterval = null, joystickActive = false;
    function connect() {
        password = document.getElementById('password').value;
        if (!password) { showToast('Введите пароль!', 'error'); return; }
        let ip = document.getElementById('pcIp').value;
        pcUrl = ip ? `http://${ip}:5000/api` : window.location.origin + '/api';
        showToast('Подключение...', 'info');
        fetch(pcUrl + '/check', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({password: password}) })
        .then(r => r.json()).then(data => {
            if (data.status === 'ok') {
                connected = true;
                document.getElementById('statusLed').classList.add('connected');
                document.getElementById('statusCard').classList.add('connected');
                document.getElementById('statusText').innerHTML = 'Подключено';
                document.getElementById('ipBadge').innerHTML = '📍 ' + (ip || 'Авто');
                document.getElementById('tabs').style.display = 'flex';
                document.getElementById('authCard').style.display = 'none';
                showToast('Подключено успешно!', 'success');
                refreshScreen(); startAutoRefresh(); getScreenSize(); loadMacros(); refreshAppVolumes(); startSystemMonitor();
            } else { showToast('Неверный пароль!', 'error'); }
        }).catch(() => { showToast('Ошибка подключения!', 'error'); });
    }
    function disconnect() { connected = false; if (refreshTimer) clearInterval(refreshTimer); document.getElementById('statusLed').classList.remove('connected'); document.getElementById('statusCard').classList.remove('connected'); document.getElementById('statusText').innerHTML = 'Не подключено'; document.getElementById('tabs').style.display = 'none'; document.getElementById('authCard').style.display = 'block'; showToast('Отключено', 'info'); }
    function showToast(msg, type) { let toast = document.createElement('div'); toast.className = 'toast'; toast.innerHTML = msg; document.body.appendChild(toast); setTimeout(() => toast.remove(), 2000); }
    function switchTab(tab) { document.querySelectorAll('.tab').forEach(t => t.classList.remove('active')); document.querySelectorAll('.panel').forEach(p => p.classList.remove('active')); event.target.closest('.tab').classList.add('active'); document.getElementById(`panel-${tab}`).classList.add('active'); }
    async function sendCommand(endpoint, data = {}) { if (!connected) return null; data.password = password; try { let res = await fetch(pcUrl + endpoint, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) }); return await res.json(); } catch(e) { return null; } }
    async function getData(endpoint) { if (!connected) return null; try { let res = await fetch(pcUrl + endpoint + '?password=' + password); return await res.json(); } catch(e) { return null; } }
    async function getScreenSize() { let data = await getData('/screen_size'); if(data) { screenWidth = data.width; screenHeight = data.height; } }
    function refreshScreen() { if (!connected) return; let img = document.getElementById('screenImg'); img.classList.add('loading'); img.src = pcUrl + '/screenshot?password=' + password + '&quality=' + currentQuality + '&t=' + Date.now(); img.onload = () => { img.classList.remove('loading'); document.getElementById('refreshTime').innerHTML = new Date().toLocaleTimeString(); }; }
    function handleScreenClick(event) { let img = document.getElementById('screenImg'); let rect = img.getBoundingClientRect(); let scaleX = screenWidth / rect.width; let scaleY = screenHeight / rect.height; let x = (event.clientX - rect.left) * scaleX; let y = (event.clientY - rect.top) * scaleY; sendCommand('/click_abs', {x: Math.round(x), y: Math.round(y), button: 'left'}); refreshScreen(); }
    function toggleAutoRefresh() { autoRefresh = !autoRefresh; document.getElementById('autoRefreshBtn').innerHTML = autoRefresh ? '<i class="fas fa-pause"></i> Пауза' : '<i class="fas fa-play"></i> Пуск'; }
    function startAutoRefresh() { if (refreshTimer) clearInterval(refreshTimer); refreshTimer = setInterval(() => { if (autoRefresh && connected) refreshScreen(); }, 2000); }
    function setQuality(quality) { currentQuality = quality; let setting = quality === 'low' ? 'Низкое' : (quality === 'high' ? 'Высокое' : 'Среднее'); document.getElementById('qualitySetting').innerHTML = setting; refreshScreen(); showToast(`Качество: ${setting}`, 'info'); }
    function sendClick(button) { sendCommand('/click', {button: button, clicks: 1}); refreshScreen(); }
    function sendScroll(amount) { sendCommand('/scroll', {amount: amount}); }
    function sendKey(key) { sendCommand('/key', {key: key}); refreshScreen(); }
    function sendType() { let text = document.getElementById('textToType').value; if(text) { sendCommand('/type', {text: text}); document.getElementById('textToType').value = ''; refreshScreen(); } }
    async function getPos() { let pos = await getData('/position'); if(pos) { document.getElementById('mouseCoords').innerHTML = `📍 X: ${pos.x}, Y: ${pos.y}`; document.getElementById('cursorPos').innerHTML = `курсор: ${pos.x},${pos.y}`; } }
    function shutdown(d) { if(confirm('Выключить компьютер?')) sendCommand('/shutdown', {delay: d}); }
    function cancelShutdown() { sendCommand('/cancel_shutdown'); }
    function lockPC() { sendCommand('/lock'); }
    function restartPC() { if(confirm('Перезагрузить компьютер?')) sendCommand('/restart'); }
    function sleepPC() { sendCommand('/sleep'); }
    function sendNotification() { sendCommand('/notify', {title: 'PC Remote', message: 'Уведомление с телефона!'}); }
    async function loadMacros() { let macros = await getData('/macros'); if(macros) { let html = ''; for(let category in macros) { html += `<div style="margin-bottom:15px;"><div style="font-size:12px; color:#00d2d3; margin-bottom:8px;">${category}</div><div class="grid-2">`; for(let app of macros[category]) { html += `<button class="btn btn-secondary" onclick="runMacro('${app.cmd}')"><i class="fas ${app.icon === '🎮' ? 'fa-gamepad' : (app.icon === '💬' ? 'fa-comment' : 'fa-apps')}"></i> ${app.name}</button>`; } html += `</div></div>`; } document.getElementById('macrosContainer').innerHTML = html; } }
    function runMacro(cmd) { sendCommand('/run_macro', {command: cmd}); refreshScreen(); }
    async function refreshAppVolumes() { let apps = await getData('/app_volumes'); if(apps) { let html = ''; for(let app of apps) { html += `<div class="metric"><span><i class="fas fa-music"></i> ${app.name}</span><input type="range" min="0" max="100" value="${app.volume}" onchange="setAppVolume('${app.name}', this.value)" style="width:120px;"><span class="metric-value">${app.volume}%</span></div>`; } document.getElementById('appVolumesContainer').innerHTML = html || '<div style="text-align:center; padding:20px;">Нет активных приложений</div>'; } }
    function setAppVolume(name, volume) { sendCommand('/set_app_volume', {name: name, volume: volume}); }
    function startSystemMonitor() { setInterval(async () => { let stats = await getData('/system_stats'); if(stats) { let tempClass = ''; if(stats.temp !== 'N/A') { if(stats.temp > 80) tempClass = 'temp-high'; else if(stats.temp > 60) tempClass = 'temp-mid'; else tempClass = 'temp-low'; } let html = `<div class="metric"><span><i class="fas fa-microchip"></i> CPU</span><span class="metric-value">${stats.cpu}%</span></div><div class="metric"><span><i class="fas fa-memory"></i> RAM</span><span class="metric-value">${stats.ram}% (${stats.ram_used}GB / ${stats.ram_total}GB)</span></div><div class="metric"><span><i class="fas fa-hdd"></i> Диск C:</span><span class="metric-value">${stats.disk}% (${stats.disk_free}GB свободно)</span></div><div class="metric"><span><i class="fas fa-temperature-high"></i> Температура CPU</span><span class="metric-value ${tempClass}">${stats.temp !== 'N/A' ? stats.temp + '°C' : 'N/A'}</span></div>`; document.getElementById('systemMetrics').innerHTML = html; } }, 2000); }
    async function askAI() { let input = document.getElementById('aiInput'); let question = input.value.trim(); if(!question) return; input.value = ''; let chatDiv = document.getElementById('chatMessages'); chatDiv.innerHTML += `<div class="message user"><div class="message-bubble">${escapeHtml(question)}</div></div>`; chatDiv.scrollTop = chatDiv.scrollHeight; let res = await sendCommand('/ai_chat', {message: question}); if(res && res.response) { chatDiv.innerHTML += `<div class="message ai"><div class="message-bubble">${escapeHtml(res.response)}</div></div>`; } else { chatDiv.innerHTML += `<div class="message ai"><div class="message-bubble">❌ Ошибка, попробуйте позже</div></div>`; } chatDiv.scrollTop = chatDiv.scrollHeight; }
    function voiceAI() { if(!('webkitSpeechRecognition' in window)) { showToast('Голос не поддерживается', 'error'); return; } let rec = new webkitSpeechRecognition(); rec.lang = 'ru-RU'; rec.onstart = () => showToast('Слушаю...', 'info'); rec.onresult = (e) => { let text = e.results[0][0].transcript; document.getElementById('aiInput').value = text; askAI(); }; rec.start(); }
    function startVoice() { if(!('webkitSpeechRecognition' in window)) { showToast('Голос не поддерживается', 'error'); return; } let rec = new webkitSpeechRecognition(); rec.lang = 'ru-RU'; rec.onstart = () => document.getElementById('voiceResult').innerHTML = '🎤 Слушаю...'; rec.onresult = (e) => { let text = e.results[0][0].transcript.toLowerCase(); document.getElementById('voiceResult').innerHTML = `🎤 "${text}"`; if(text.includes('выключи')) shutdown(30); else if(text.includes('отмена')) cancelShutdown(); else if(text.includes('блокнот')) sendCommand('/open_app', {path: 'notepad.exe'}); else if(text.includes('калькулятор')) sendCommand('/open_app', {path: 'calc.exe'}); else if(text.includes('громче')) sendCommand('/volume', {action: 'up'}); else if(text.includes('тише')) sendCommand('/volume', {action: 'down'}); else if(text.includes('мут')) sendCommand('/volume', {action: 'mute'}); else sendCommand('/type', {text: text}); refreshScreen(); }; rec.start(); }
    function changePassword() { let newPass = prompt('Введите новый пароль:'); if(newPass && newPass.length >= 4) { sendCommand('/change_password', {new_password: newPass}); password = newPass; showToast('Пароль изменён!', 'success'); } }
    function escapeHtml(text) { let div = document.createElement('div'); div.textContent = text; return div.innerHTML; }
    const area = document.getElementById('joystickArea'); const handle = document.getElementById('joystickHandle');
    if(area) {
        function handleMove(x, y) { let rect = area.getBoundingClientRect(); let cx = rect.left + rect.width/2; let cy = rect.top + rect.height/2; let dx = x - cx; let dy = y - cy; let max = rect.width/2 - 35; let dist = Math.min(Math.sqrt(dx*dx + dy*dy), max); let angle = Math.atan2(dy, dx); let hx = Math.cos(angle) * dist; let hy = Math.sin(angle) * dist; handle.style.transform = `translate(${hx}px, ${hy}px)`; if(moveInterval) clearInterval(moveInterval); let speed = dist / max; moveInterval = setInterval(() => { let mx = Math.cos(angle) * speed * 20; let my = Math.sin(angle) * speed * 20; sendCommand('/move_rel', {dx: mx, dy: my}); }, 30); }
        function resetJoy() { handle.style.transform = 'translate(0,0)'; if(moveInterval) clearInterval(moveInterval); moveInterval = null; }
        area.addEventListener('touchstart', (e) => { e.preventDefault(); joystickActive = true; let t = e.touches[0]; handleMove(t.clientX, t.clientY); });
        area.addEventListener('touchmove', (e) => { e.preventDefault(); if(joystickActive) { let t = e.touches[0]; handleMove(t.clientX, t.clientY); } });
        area.addEventListener('touchend', () => { joystickActive = false; resetJoy(); });
    }
    setInterval(getPos, 2000);
    fetch('/api/public_url').then(r=>r.json()).then(d=>{ if(d.url) { document.getElementById('publicUrlCard').style.display = 'block'; document.getElementById('publicUrl').innerHTML = `<i class="fas fa-link"></i> ${d.url}`; } }).catch(()=>{});
</script>
</body>
</html>'''

# ============= API КОМАНДЫ (ВЕБ) =============

def check_auth(data=None):
    if data and data.get('password') == PASSWORD:
        return True
    if request.args and request.args.get('password') == PASSWORD:
        return True
    if request.json and request.json.get('password') == PASSWORD:
        return True
    return False

@app.route('/')
def index():
    return HTML

@app.route('/api/check', methods=['POST'])
def check():
    data = request.json
    if data.get('password') == PASSWORD:
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 403

@app.route('/api/public_url')
def public_url():
    return jsonify({'url': PUBLIC_URL if 'PUBLIC_URL' in globals() else ''})

@app.route('/api/screenshot')
def screenshot():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403
    quality = request.args.get('quality', 'medium')
    if quality == 'low':
        jpeg_quality = 30
        resize = 0.5
    elif quality == 'high':
        jpeg_quality = 90
        resize = 1
    else:
        jpeg_quality = 60
        resize = 0.7
    screenshot = pyautogui.screenshot()
    if resize != 1:
        width = int(screenshot.width * resize)
        height = int(screenshot.height * resize)
        screenshot = screenshot.resize((width, height), Image.Resampling.LANCZOS)
    img_io = io.BytesIO()
    screenshot.save(img_io, 'JPEG', quality=jpeg_quality, optimize=True)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.route('/api/screen_size')
def screen_size():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403
    s = pyautogui.size()
    return jsonify({'width': s.width, 'height': s.height})

@app.route('/api/position')
def position():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403
    p = pyautogui.position()
    return jsonify({'x': p.x, 'y': p.y})

@app.route('/api/click_abs', methods=['POST'])
def click_abs():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    pyautogui.click(x=data.get('x', 0), y=data.get('y', 0), button=data.get('button', 'left'))
    return jsonify({'ok': True})

@app.route('/api/move_rel', methods=['POST'])
def move_rel():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    pyautogui.moveRel(data.get('dx', 0), data.get('dy', 0))
    return jsonify({'ok': True})

@app.route('/api/click', methods=['POST'])
def click():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    pyautogui.click(button=data.get('button', 'left'), clicks=data.get('clicks', 1))
    return jsonify({'ok': True})

@app.route('/api/scroll', methods=['POST'])
def scroll():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    pyautogui.scroll(data.get('amount', 0))
    return jsonify({'ok': True})

@app.route('/api/key', methods=['POST'])
def key():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    keyboard.press_and_release(data.get('key', ''))
    return jsonify({'ok': True})

@app.route('/api/type', methods=['POST'])
def type_text():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    text = data.get('text', '')
    if text:
        try:
            pyautogui.write(text)
        except:
            try:
                keyboard.write(text)
            except:
                for char in text:
                    keyboard.press_and_release(char)
                    time.sleep(0.01)
    return jsonify({'ok': True})

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    os.system(f'shutdown /s /t {data.get("delay", 60)}')
    return jsonify({'ok': True})

@app.route('/api/cancel_shutdown', methods=['POST'])
def cancel_shutdown():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    os.system('shutdown /a')
    return jsonify({'ok': True})

@app.route('/api/restart', methods=['POST'])
def restart():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    os.system('shutdown /r /t 10')
    return jsonify({'ok': True})

@app.route('/api/sleep', methods=['POST'])
def sleep():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    return jsonify({'ok': True})

@app.route('/api/lock', methods=['POST'])
def lock_pc():
    if not check_auth(request.json):
        return jsonify({'error': 'Unauthorized'}), 403
    os.system('rundll32.exe user32.dll,LockWorkStation')
    return jsonify({'ok': True})

@app.route('/api/notify', methods=['POST'])
def notify():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        from plyer import notification
        notification.notify(title=data.get('title', 'PC Remote'), message=data.get('message', ''), timeout=3)
    except:
        pass
    return jsonify({'ok': True})

@app.route('/api/volume', methods=['POST'])
def volume():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    a = data.get('action', '')
    if a == 'up':
        keyboard.press_and_release('volume up')
    elif a == 'down':
        keyboard.press_and_release('volume down')
    elif a == 'mute':
        keyboard.press_and_release('volume mute')
    return jsonify({'ok': True})

@app.route('/api/open_app', methods=['POST'])
def open_app():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        os.startfile(data.get('path', ''))
    except:
        subprocess.Popen(data.get('path', ''), shell=True)
    return jsonify({'ok': True})

@app.route('/api/macros')
def macros():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(QUICK_COMMANDS)

@app.route('/api/run_macro', methods=['POST'])
def run_macro():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    cmd = data.get('command', '')
    if cmd == 'lock':
        os.system('rundll32.exe user32.dll,LockWorkStation')
    elif cmd == 'sleep':
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    elif cmd == 'restart':
        os.system('shutdown /r /t 10')
    else:
        subprocess.Popen(cmd, shell=True)
    return jsonify({'ok': True})

@app.route('/api/app_volumes')
def app_volumes():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403
    apps = []
    try:
        from pycaw.pycaw import AudioUtilities
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name():
                volume = session.SimpleAudioVolume
                if volume:
                    apps.append({
                        'name': session.Process.name(),
                        'volume': int(volume.GetMasterVolume() * 100)
                    })
    except:
        apps = [{'name': 'Главный канал', 'volume': 50}]
    return jsonify(apps[:10])

@app.route('/api/set_app_volume', methods=['POST'])
def set_app_volume():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        from pycaw.pycaw import AudioUtilities
        name = data.get('name', '')
        volume = data.get('volume', 50) / 100
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == name:
                session.SimpleAudioVolume.SetMasterVolume(volume, None)
                break
    except:
        pass
    return jsonify({'ok': True})

@app.route('/api/system_stats')
def system_stats():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    ram_used_gb = round(ram.used / (1024**3), 1)
    ram_total_gb = round(ram.total / (1024**3), 1)
    try:
        disk = psutil.disk_usage('C:')
        disk_percent = disk.percent
        disk_free_gb = round(disk.free / (1024**3), 1)
    except:
        disk_percent = 0
        disk_free_gb = 0
    temp = get_cpu_temperature()
    return jsonify({
        'cpu': cpu,
        'ram': ram.percent,
        'ram_used': ram_used_gb,
        'ram_total': ram_total_gb,
        'disk': disk_percent,
        'disk_free': disk_free_gb,
        'temp': temp
    })

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    message = data.get('message', '').lower()
    responses = {
        'привет': 'Привет! Я DeepSeek AI. Чем могу помочь?',
        'как дела': 'Всё отлично! Управляю ПК в лучшем виде 😊',
        'помощь': 'Я могу управлять мышью, клавиатурой, открывать программы, выключать ПК и многое другое!',
        'выключи': 'Выключаю компьютер через 30 секунд. Скажи "отмена" если передумал.',
        'перезагрузи': 'Перезагружаю компьютер через 10 секунд!',
        'блокнот': 'Открываю Блокнот!',
        'калькулятор': 'Запускаю Калькулятор!',
        'температура': f'Температура процессора: {get_cpu_temperature()}°C',
    }
    for key, resp in responses.items():
        if key in message:
            return jsonify({'response': resp})
    return jsonify({'response': f'Получил: "{message}".\n\nСкажи "помощь" чтобы узнать что я умею!'})

@app.route('/api/change_password', methods=['POST'])
def change_password():
    global PASSWORD
    data = request.json
    if not check_auth(data):
        return jsonify({'error': 'Unauthorized'}), 403
    PASSWORD = data.get('new_password', PASSWORD)
    return jsonify({'ok': True})

# ============= ЗАПУСК ТУННЕЛЯ =============
PUBLIC_URL = ""

def start_ngrok():
    global PUBLIC_URL
    try:
        if not os.path.exists('ngrok.exe'):
            print("📥 Скачиваю ngrok...")
            import urllib.request
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
            urllib.request.urlretrieve(url, "ngrok.zip")
            import zipfile
            with zipfile.ZipFile("ngrok.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.remove("ngrok.zip")
        subprocess.Popen(['ngrok', 'http', '5000', '--log=stdout'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()
        PUBLIC_URL = tunnels['tunnels'][0]['public_url']
        print(f"\n🌍 ПУБЛИЧНЫЙ ДОСТУП: {PUBLIC_URL}")
        print(f"🔐 Пароль: {PASSWORD}")
    except Exception as e:
        print(f"⚠️ Ngrok не запущен: {e}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def run_telegram_bot():
    """Запуск Telegram бота в отдельном потоке"""
    tg_app = Application.builder().token(TELEGRAM_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", tg_start))
    tg_app.add_handler(CommandHandler("cancel", tg_cancel))
    tg_app.add_handler(CallbackQueryHandler(tg_button_callback))
    tg_app.add_handler(MessageHandler(None, tg_handle_message))
    print("🤖 TELEGRAM БОТ ЗАПУЩЕН!")
    tg_app.run_polling()

# ============= ЗАПУСК =============
if __name__ == '__main__':
    ip = get_local_ip()
    print('\n' + '═' * 60)
    print('╔══════════════════════════════════════════════════════════════╗')
    print('║  🚀 PC REMOTE CONTROL PRO v7.0 - С TELEGRAM БОТОМ!          ║')
    print('║  🔥 УПРАВЛЕНИЕ ПК: САЙТ + TELEGRAM + ТЕЛЕФОН               ║')
    print('╚══════════════════════════════════════════════════════════════╝')
    print('═' * 60)
    print(f'\n📱 ЛОКАЛЬНЫЙ ДОСТУП (САЙТ): http://{ip}:5000')
    print(f'🤖 TELEGRAM БОТ: @{TELEGRAM_TOKEN.split(":")[0]}')
    print(f'🔐 ПАРОЛЬ ДЛЯ САЙТА: {PASSWORD}')
    print('\n✨ ВОЗМОЖНОСТИ:')
    print('   🖥️  Веб-сайт с экраном ПК и джойстиком')
    print('   🤖 Telegram бот с кнопками')
    print('   🎮 Запуск игр и программ')
    print('   📊 Мониторинг системы и температура')
    print('   🎤 Голосовые команды')
    print('   🌍 Доступ из любой сети через ngrok')
    print('═' * 60 + '\n')
    
    # Запускаем Telegram бота в отдельном потоке
    tg_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    tg_thread.start()
    
    # Запускаем ngrok
    threading.Thread(target=start_ngrok, daemon=True).start()
    
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)