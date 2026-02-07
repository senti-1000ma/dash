from flask import Flask, send_from_directory, render_template_string
from flask_socketio import SocketIO, emit
import threading
import time
import json
import os

# Flask 앱 및 SocketIO 초기화
app = Flask(__name__)
# 보안상의 이유로 실제 환경에서는 더 강력한 비밀 키를 사용해야 합니다.
app.config['SECRET_KEY'] = 'a_very_secret_key_for_dashboard_12345' 
socketio = SocketIO(app)

# --- 대시보드에 표시될 데이터 ---
# 현재 제 환경에서 직접 접근하여 실시간으로 가져오기 어려운 정보는
# 'N/A' 또는 '플랫폼 API 필요'와 같이 표시됩니다.
dashboard_data = {
    "model": "google/gemini-2.5-flash-lite",
    "current_task": "대시보드 초기화 중...",
    "token_count": "N/A (플랫폼 API 필요)",
    "estimated_cost": "N/A (플랫폼 API 필요)"
}

# --- 실시간 업데이트를 위한 백그라운드 스레드 ---
def background_update_task():
    """
    백그라운드에서 주기적으로 데이터를 업데이트하고 클라이언트에게 전송하는 함수입니다.
    """
    print("백그라운드 업데이트 작업 시작...")
    while True:
        # --- 여기에 실시간으로 업데이트할 로직을 추가합니다 ---
        # 예: 현재 시간을 기반으로 작업 상태를 업데이트
        current_time_str = time.strftime("%Y-%m-%d %H:%M:%S GMT%z")
        
        # 실제 작업 내용을 반영하려면 이 부분을 동적으로 업데이트해야 합니다.
        # 예를 들어, 대화 내용이나 수행 중인 작업에 따라 'current_task' 값을 변경할 수 있습니다.
        # 여기서는 예시로 시간 정보와 함께 '모니터링 중'으로 표시합니다.
        dashboard_data["current_task"] = f"시스템 모니터링 중 ({current_time_str})"
        
        # 업데이트된 데이터를 모든 연결된 클라이언트에게 전송
        socketio.emit('update', dashboard_data)
        
        time.sleep(10) # 10초마다 업데이트

# --- Flask 라우트 설정 ---

# 메인 페이지 (index.html)를 제공하는 라우트
@app.route('/')
def index():
    # static 폴더에서 index.html을 제공합니다.
    return send_from_directory('static', 'index.html')

# static 폴더 내의 다른 파일들(CSS, JS 등)을 제공하는 라우트
@app.route('/static/<path:filename>')
def serve_static_files(filename):
    return send_from_directory('static', filename)

# --- SocketIO 이벤트 핸들러 ---

# 클라이언트가 연결되었을 때 호출됩니다.
@socketio.on('connect')
def handle_connect():
    print('클라이언트가 연결되었습니다.')
    # 연결된 클라이언트에게 즉시 최신 데이터 전송
    emit('update', dashboard_data)

# 클라이언트가 연결을 끊었을 때 호출됩니다.
@socketio.on('disconnect')
def handle_disconnect():
    print('클라이언트가 연결을 끊었습니다.')

# --- 메인 실행 부분 ---
if __name__ == '__main__':
    # 백그라운드 업데이트 스레드 시작
    update_thread = threading.Thread(target=background_update_task)
    update_thread.daemon = True # 메인 스레드 종료 시 함께 종료되도록 설정
    update_thread.start()

    # static 폴더 생성 (index.html이 저장될 곳)
    if not os.path.exists('static'):
        os.makedirs('static')

    # Flask 앱 실행
    print("Flask 대시보드 서버 시작: http://127.0.0.1:5000")
    # host='0.0.0.0' 설정으로 로컬 네트워크 내 다른 기기에서도 접근 가능하게 합니다.
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
