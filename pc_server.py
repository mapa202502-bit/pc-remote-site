from flask import Flask, render_template_string, request, jsonify
import requests
import os

app = Flask(__name__)

# Токен твоего Telegram бота (нужен для отправки команд на ПК)
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"  # Вставь сюда токен от @BotFather
PC_CHAT_ID = -123456789  # ID секретной группы (где бот и программа на ПК)

# HTML интерфейс
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>PC Remote Control</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 500px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 20px; font-size: 24px; }
        .status {
            background: #0f3460;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
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
        button:active { transform: scale(0.95); }
        .info {
            text-align: center;
            font-size: 12px;
            color: #aaa;
            margin-top: 20px;
        }
        .success { background: #00b894; }
        .danger { background: #ff4757; }
        .warning { background: #ffa502; }
    </style>
</head>
<body>
<div class="container">
    <h1>🖥️ PC REMOTE CONTROL</h1>
    <div class="status" id="status">🌐 Сайт работает!</div>
    
    <div class="grid">
        <button class="danger" onclick="sendCmd('shutdown')">🔌 ВЫКЛЮЧЕНИЕ</button>
        <button class="warning" onclick="sendCmd('restart')">🔄 ПЕРЕЗАГРУЗКА</button>
        <button onclick="sendCmd('lock')">🔒 БЛОКИРОВКА</button>
        <button onclick="sendCmd('sleep')">💤 СОН</button>
        <button onclick="sendCmd('cancel')">❌ ОТМЕНА</button>
        <button onclick="sendCmd('screenshot')">📸 СКРИНШОТ</button>
        <button onclick="sendCmd('run_notepad')">📝 БЛОКНОТ</button>
        <button onclick="sendCmd('run_calc')">🧮 КАЛЬКУЛЯТОР</button>
        <button onclick="sendCmd('volume_up')">🔊 ГРОМКОСТЬ +</button>
        <button onclick="sendCmd('volume_down')">🔉 ГРОМКОСТЬ -</button>
        <button onclick="sendCmd('click_left')">🖱️ ЛЕВЫЙ КЛИК</button>
        <button onclick="sendCmd('click_right')">🖱️ ПРАВЫЙ КЛИК</button>
    </div>
    
    <div class="info">
        ⚠️ Команды отправляются через Telegram бота.<br>
        На ПК должна быть запущена программа-слушатель.
    </div>
</div>

<script>
function sendCmd(cmd) {
    let status = document.getElementById('status');
    status.innerHTML = '⏳ Отправка команды...';
    status.style.background = '#ffa502';
    
    fetch('/api/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({command: cmd})
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'ok') {
            status.innerHTML = '✅ Команда отправлена: ' + cmd;
            status.style.background = '#00b894';
            setTimeout(() => {
                status.innerHTML = '🌐 Сайт работает!';
                status.style.background = '#0f3460';
            }, 2000);
        } else {
            status.innerHTML = '❌ Ошибка: ' + (data.error || 'неизвестная');
            status.style.background = '#ff4757';
        }
    })
    .catch(err => {
        status.innerHTML = '❌ Ошибка соединения';
        status.style.background = '#ff4757';
    });
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/api/send', methods=['POST'])
def send_command():
    """Отправляет команду через Telegram бота на ПК"""
    data = request.json
    command = data.get('command')
    
    if not command:
        return jsonify({'status': 'error', 'error': 'Нет команды'}), 400
    
    try:
        # Отправляем команду в секретную группу Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": PC_CHAT_ID,
            "text": command
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return jsonify({'status': 'ok', 'command': command})
        else:
            return jsonify({'status': 'error', 'error': 'Telegram API error'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/health')
def health():
    """Для пинга (чтобы Render не уснул)"""
    return jsonify({'status': 'alive'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
