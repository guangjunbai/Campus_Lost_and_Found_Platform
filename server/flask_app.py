from flask import Flask, request, jsonify
import sqlite3
import hashlib
import secrets

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)