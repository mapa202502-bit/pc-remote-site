# pc-remote-site
pc-remote-site
from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

# HTML интерфейс (упрощённая версия)
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Remote Control</title>
    <style>
        body {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
        }
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        button {
            background: #e94560;
            border: none;
            color: white;
            padding: 15px;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        button:active {
            transform: scale(0.95);
        }
        .info {
            text-align: center;
            font-size: 12px;
            color: #aaa;
            margin-top: 20px;
        }
        .status {
            background: #0f3460;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .online {
            color: #00d2d3;
            font-weight: bold;
        }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <h1>🖥️ PC REMOTE CONTROL</h1>
        <div class="status" id="status">
            🌐 Сайт работает!
        </div>
        <div class="grid">
            <button onclick="sendCommand('shutdown')">🔌 ВЫКЛЮЧЕНИЕ</button>
            <button onclick="sendCommand('restart')">🔄 ПЕРЕЗАГРУЗКА</button>
            <button onclick="sendCommand('lock')">🔒 БЛОКИРОВКА</button>
            <button onclick="sendCommand('sleep')">💤 СОН</button>
            <button onclick="sendCommand('notepad')">📝 БЛОКНОТ</button>
            <button onclick="sendCommand('calc')">🧮 КАЛЬКУЛЯТОР</button>
        </div>
        <div class="info">
            ⚠️ Команды будут выполняться на ПК только если<br>
            на нём запущена программа-агент и настроен туннель
        </div>
    </div>
</div>

<script>
    function sendCommand(cmd) {
        fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: cmd})
        })
        .then(response => response.json())
        .then(data => {
            let status = document.getElementById('status');
            if(data.status === 'ok') {
                status.innerHTML = '✅ Команда отправлена: ' + cmd;
                status.style.background = '#00b894';
                setTimeout(() => {
                    status.innerHTML = '🌐 Сайт работает!';
                    status.style.background = '#0f3460';
                }, 2000);
            } else {
                status.innerHTML = '❌ Ошибка: ' + (data.error || 'ПК не подключён');
                status.style.background = '#ff4757';
            }
        })
        .catch(() => {
            document.getElementById('status').innerHTML = '❌ Ошибка соединения';
        });
    }
</script>
</body>
</html>
'''

# Хранилище команд для ПК (в реальном проекте используй БД или Redis)
commands_queue = []

@app.route('/')
def index():
    return HTML

@app.route('/api/command', methods=['POST'])
def receive_command():
    """Принимает команду с сайта"""
    data = request.json
    command = data.get('command')
    if command:
        commands_queue.append(command)
        return jsonify({'status': 'ok', 'command': command})
    return jsonify({'status': 'error', 'error': 'Нет команды'}), 400

@app.route('/api/poll', methods=['GET'])
def poll_commands():
    """ПК забирает команды отсюда"""
    if commands_queue:
        command = commands_queue.pop(0)
        return jsonify({'command': command})
    return jsonify({'command': None})

@app.route('/api/health', methods=['GET'])
def health():
    """Для пинга (чтобы Render не уснул)"""
    return jsonify({'status': 'alive'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
