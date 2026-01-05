#!/usr/bin/env python3
"""
Web Interface cho Ứng dụng Tự động hóa AI
Giao diện web đơn giản cho người non-tech
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
from dotenv import load_dotenv
import threading

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variable to track automation status
automation_status = {
    'running': False,
    'logs': [],
    'success': None
}

def get_input_file_path():
    """Lấy đường dẫn đến file input.json"""
    return os.path.join(os.path.dirname(__file__), "input.json")

@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/api/load-config', methods=['GET'])
def load_config():
    """Load config hiện tại từ input.json"""
    input_path = get_input_file_path()

    if os.path.exists(input_path):
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return jsonify({
                'success': True,
                'config': config
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Lỗi đọc file: {str(e)}'
            })
    else:
        return jsonify({
            'success': False,
            'error': 'File input.json không tồn tại'
        })

@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Lưu config vào input.json"""
    try:
        config = request.json
        input_path = get_input_file_path()

        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'message': 'Đã lưu cấu hình thành công!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi lưu file: {str(e)}'
        })

@app.route('/api/upload-config', methods=['POST'])
def upload_config():
    """Upload file input.json"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Không có file được upload'
        })

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Chưa chọn file'
        })

    try:
        # Validate JSON
        content = file.read().decode('utf-8')
        config = json.loads(content)

        # Save to input.json
        input_path = get_input_file_path()
        with open(input_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'message': 'Đã upload file thành công!',
            'config': config
        })
    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': 'File không đúng định dạng JSON'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi upload file: {str(e)}'
        })

@app.route('/api/run-automation', methods=['POST'])
def run_automation():
    """Chạy automation"""
    global automation_status

    if automation_status['running']:
        return jsonify({
            'success': False,
            'error': 'Automation đang chạy!'
        })

    input_path = get_input_file_path()

    if not os.path.exists(input_path):
        return jsonify({
            'success': False,
            'error': 'Chưa có file input.json. Vui lòng tạo hoặc upload file cấu hình!'
        })

    # Reset status
    automation_status = {
        'running': True,
        'logs': ['🚀 Bắt đầu automation...'],
        'success': None
    }

    # Run automation in background thread
    thread = threading.Thread(target=run_automation_background, args=(input_path,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Đã bắt đầu automation!'
    })

def run_automation_background(input_path):
    """Chạy automation trong background"""
    global automation_status

    try:
        from features.csp.csp_admin import main as csp_main

        automation_status['logs'].append('📂 Đang tải cấu hình...')

        # Run automation
        success = csp_main(input_file=input_path)

        automation_status['success'] = success

        if success:
            automation_status['logs'].append('✅ Automation hoàn thành thành công!')
        else:
            automation_status['logs'].append('⚠️ Automation hoàn thành với lỗi!')

    except Exception as e:
        automation_status['success'] = False
        automation_status['logs'].append(f'❌ Lỗi: {str(e)}')

    finally:
        automation_status['running'] = False

@app.route('/api/automation-status', methods=['GET'])
def get_automation_status():
    """Lấy trạng thái automation"""
    return jsonify(automation_status)

@app.route('/api/download-template', methods=['GET'])
def download_template():
    """Download file template"""
    template = {
        "admin_credentials": {
            "username": "admin_username",
            "password": "admin_password",
            "csp_admin_url": "https://csp-portal.com/portal/users/list"
        },
        "users": [
            {
                "target_user": "user1@example.com",
                "new_role": "CSP-RB-TELLER",
                "branch_hierarchy": ["VIB Bank", "North", "002_HA NOI"]
            }
        ]
    }

    template_path = os.path.join(os.path.dirname(__file__), "template.json")
    with open(template_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    return send_file(template_path, as_attachment=True, download_name='input_template.json')

if __name__ == '__main__':
    PORT = 5000
    print("🌐 Starting Web Interface...")
    print(f"📱 Open browser: http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=PORT)
