from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
import eventlet

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Храним подключённые ПК
connected_pcs = {}

# HTML интерфейс
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Remote Control</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
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
        h1 { text-align: center; margin-bottom: 20px; }
        .status {
            background: #0f3460;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .status.online { background: #00b894; }
        .section {
            background: rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #00d2d3;
        }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        button {
            background: #e94560;
            border: none;
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
        }
        button:active { transform: scale(0.95); }
        .danger { background: #ff4757; }
        .warning { background: #ffa502; }
        .info { background: #00d2d3; color: #1a1a2e; }
        .info-text { text-align: center; font-size: 12px; color: #aaa; margin-top: 20px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🖥️ PC REMOTE CONTROL</h1>
    <div class="status" id="status">🔌 ПК не подключён</div>

    <div class="section">
        <div class="section-title">🎮 ПРОГРАММЫ</div>
        <div class="grid">
            <button class="info" onclick="sendCmd('run_exloader')">⚡ EXLOADER</button>
            <button onclick="sendCmd('run_steam')">🎮 STEAM</button>
            <button onclick="sendCmd('run_discord')">💬 DISCORD</button>
            <button onclick="sendCmd('run_chrome')">🌐 CHROME</button>
            <button onclick="sendCmd('run_notepad')">📝 БЛОКНОТ</button>
            <button onclick="sendCmd('run_calc')">🧮 КАЛЬКУЛЯТОР</button>
        </div>
    </div>

    <div class="section">
        <div class="section-title">🔧 УПРАВЛЕНИЕ ПК</div>
        <div class="grid">
            <button class="danger" onclick="sendCmd('shutdown')">🔌 ВЫКЛЮЧЕНИЕ</button>
            <button class="warning" onclick="sendCmd('restart')">🔄 ПЕРЕЗАГРУЗКА</button>
            <button onclick="sendCmd('lock')">🔒 БЛОКИРОВКА</button>
            <button onclick="sendCmd('sleep')">💤 СОН</button>
            <button onclick="sendCmd('cancel')">❌ ОТМЕНА</button>
            <button onclick="sendCmd('screenshot')">📸 СКРИНШОТ</button>
        </div>
    </div>

    <div class="section">
        <div class="section-title">🔊 ЗВУК</div>
        <div class="grid">
            <button onclick="sendCmd('volume_up')">🔊 ГРОМКОСТЬ +</button>
            <button onclick="sendCmd('volume_down')">🔉 ГРОМКОСТЬ -</button>
            <button onclick="sendCmd('volume_mute')">🔇 MUTE</button>
        </div>
    </div>

    <div class="section">
        <div class="section-title">🖱️ МЫШЬ</div>
        <div class="grid">
            <button onclick="sendCmd('click_left')">🖱️ ЛЕВЫЙ КЛИК</button>
            <button onclick="sendCmd('click_right')">🖱️ ПРАВЫЙ КЛИК</button>
        </div>
    </div>

    <div class="info-text">
        ⚠️ Команды отправляются напрямую на ПК через WebSocket.<br>
        На ПК должна быть запущена программа-клиент.
    </div>
</div>

<script>
const socket = io();
let pcConnected = false;

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('pc_status', (data) => {
    if(data.connected) {
        pcConnected = true;
        document.getElementById('status').innerHTML = '🟢 ПК подключён!';
        document.getElementById('status').classList.add('online');
    } else {
        pcConnected = false;
        document.getElementById('status').innerHTML = '🔴 ПК НЕ ПОДКЛЮЧЁН';
        document.getElementById('status').classList.remove('online');
    }
});

socket.on('command_result', (data) => {
    console.log('Result:', data);
    if(data.result === 'screenshot') {
        const img = document.createElement('img');
        img.src = data.image;
        img.style.maxWidth = '100%';
        img.style.marginTop = '10px';
        img.style.borderRadius = '10px';
        document.getElementById('status').after(img);
        setTimeout(() => img.remove(), 5000);
    } else {
        const status = document.getElementById('status');
        status.innerHTML = '✅ ' + data.result;
        status.style.background = '#00b894';
        setTimeout(() => {
            if(pcConnected) {
                status.innerHTML = '🟢 ПК подключён!';
                status.style.background = '#0f3460';
            } else {
                status.innerHTML = '🔴 ПК НЕ ПОДКЛЮЧЁН';
            }
        }, 2000);
    }
});

function sendCmd(cmd) {
    if(!pcConnected) {
        alert('ПК не подключён! Запусти программу на ПК');
        return;
    }
    socket.emit('command', {cmd: cmd});
    const status = document.getElementById('status');
    status.innerHTML = '⏳ Отправка: ' + cmd;
    status.style.background = '#ffa502';
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('pc_register')
def handle_pc_register(data):
    """ПК регистрируется на сервере"""
    connected_pcs[request.sid] = data
    print(f"PC connected: {data}")
    emit('pc_status', {'connected': True}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_pcs:
        del connected_pcs[request.sid]
        print(f"PC disconnected: {request.sid}")
        emit('pc_status', {'connected': False}, broadcast=True)

@socketio.on('command')
def handle_command(data):
    """Команда с сайта -> пересылаем ПК"""
    cmd = data.get('cmd')
    if connected_pcs:
        # Отправляем команду первому подключённому ПК
        emit('execute', {'cmd': cmd}, room=list(connected_pcs.keys())[0])
    else:
        emit('command_result', {'result': 'No PC connected'})

@socketio.on('command_result')
def handle_result(data):
    """Результат с ПК -> пересылаем сайту"""
    emit('command_result', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
