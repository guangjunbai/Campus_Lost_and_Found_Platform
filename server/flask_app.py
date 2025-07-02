from flask import Flask, request, jsonify, session
import sqlite3
import hashlib
import secrets
from werkzeug.utils import secure_filename
import time as pytime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 session 加密，实际项目请用更复杂的密钥

DB_PATH = r"D:\SqliteDatabase\user.db"  # 改成你的真实路径


def hash_password(pwd: str, salt: str) -> str:
    """将密码和盐组合后哈希"""
    return hashlib.sha256((pwd + salt).encode()).hexdigest()


def get_database_connection():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def validate_request_data(data: dict) -> tuple[bool, str, str]:
    """验证请求数据"""
    username = data.get('username')
    password = data.get('password')
    
    if not username:
        return False, "用户名不能为空", ""
    
    if not password:
        return False, "密码不能为空", ""
    
    return True, username, password


def get_user_from_database(username: str) -> tuple[bool, str, tuple]:
    """从数据库获取用户信息"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT salt, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return True, "", result
    except Exception as e:
        return False, f"数据库错误: {e}", None


def verify_user_credentials(username: str, password: str) -> tuple[bool, str]:
    """验证用户凭据"""
    # 1. 从数据库获取用户信息
    success, error_msg, result = get_user_from_database(username)
    if not success:
        return False, error_msg
    
    # 2. 检查用户是否存在
    if not result:
        return False, "用户不存在"
    
    # 3. 验证密码
    salt, correct_hash = result
    if hash_password(password, salt) == correct_hash:
        return True, "登录成功"
    else:
        return False, "密码错误"


def check_user_exists(username: str) -> tuple[bool, str]:
    """检查用户是否已存在"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, "用户已存在"
        else:
            return False, ""
    except Exception as e:
        return False, f"数据库错误: {e}"


def create_user(username: str, password: str) -> tuple[bool, str]:
    """创建新用户"""
    try:
        # 生成盐值
        salt = secrets.token_hex(16)
        # 哈希密码
        password_hash = hash_password(password, salt)
        
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        conn.commit()
        conn.close()
        
        return True, "用户创建成功"
    except Exception as e:
        return False, f"创建用户失败: {e}"


def get_user_id_by_username(username: str) -> int:
    """通过用户名查找用户ID"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        return None


@app.route('/api/login', methods=['POST'])
def login():
    """登录API接口"""
    # 1. 获取并验证请求数据
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "无效的请求数据"}), 400
    
    is_valid, username, password = validate_request_data(data)
    if not is_valid:
        return jsonify({"success": False, "message": username}), 400
    
    # 2. 验证用户凭据
    success, message = verify_user_credentials(username, password)
    
    # 3. 返回结果
    if success:
        # 登录成功，写入 session
        user_id = get_user_id_by_username(username)
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 401


@app.route('/api/register', methods=['POST'])
def register():
    """注册API接口"""
    # 1. 获取并验证请求数据
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "无效的请求数据"}), 400
    
    is_valid, username, password = validate_request_data(data)
    if not is_valid:
        return jsonify({"success": False, "message": username}), 400
    
    # 2. 检查用户名长度
    if len(username) < 3:
        return jsonify({"success": False, "message": "用户名长度至少3个字符"}), 400
    
    # 3. 检查密码长度
    if len(password) < 6:
        return jsonify({"success": False, "message": "密码长度至少6个字符"}), 400
    
    # 4. 检查用户是否已存在
    exists, error_msg = check_user_exists(username)
    if exists:
        return jsonify({"success": False, "message": error_msg}), 409
    
    # 5. 创建新用户
    success, message = create_user(username, password)
    
    # 6. 返回结果
    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 500


@app.route('/api/post', methods=['POST'])
def post_info():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "未登录，无法发帖"})
    item_name = request.form.get('item_name')
    item_category = request.form.get('item_category')
    item_type = request.form.get('type')
    description = request.form.get('description')
    time_ = request.form.get('time')
    location = request.form.get('location')
    image = request.files.get('image')
    image_path = None

    if not item_name or not location:
        return jsonify({"success": False, "message": "缺少必填项"})

    if image:
        filename = secure_filename(image.filename)
        unique_filename = f"{int(pytime.time())}_{filename}"
        save_dir = os.path.join(os.path.dirname(__file__), "../data/uploads")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, unique_filename)
        image.save(save_path)
        image_path = f"data/uploads/{unique_filename}"

    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, type, item_name, item_category, description, image_path, time, location, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (
                user_id,  # 从 session 获取 user_id
                item_type,
                item_name,
                item_category,
                description,
                image_path,
                time_,
                location,
                'active'
            )
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "发布成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)