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


@app.route('/api/get_lost_items', methods=['GET'])
def get_lost_items():
    """获取失物招领信息列表，支持关键字搜索"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '').strip()
        item_type = request.args.get('type', '')  # 可选：按类型筛选
        category = request.args.get('category', '')  # 可选：按分类筛选
        limit = request.args.get('limit', 50, type=int)  # 限制返回数量
        offset = request.args.get('offset', 0, type=int)  # 分页偏移

        conn = get_database_connection()
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = ["1=1"]  # 始终为真的条件，便于动态拼接
        params = []

        if keyword:
            # 使用LIKE进行模糊搜索，支持物品名称、描述、地点
            where_conditions.append("""
                (item_name LIKE ? OR description LIKE ? OR location LIKE ?)
            """)
            keyword_param = f"%{keyword}%"
            params.extend([keyword_param, keyword_param, keyword_param])

        if item_type:
            where_conditions.append("type = ?")
            params.append(item_type)

        if category:
            where_conditions.append("item_category = ?")
            params.append(category)

        # 构建完整的SQL查询
        sql = f"""
            SELECT 
                p.id,
                p.item_name,
                p.item_category,
                p.type,
                p.description,
                p.image_path,
                p.time,
                p.location,
                p.status,
                p.created_at,
                u.username as publisher
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE {' AND '.join(where_conditions)}
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """

        params.extend([limit, offset])

        # 执行查询
        cursor.execute(sql, params)
        results = cursor.fetchall()

        # 转换为字典列表
        items = []
        for row in results:
            item = {
                'id': row[0],
                'item_name': row[1],
                'item_category': row[2],
                'type': row[3],
                'description': row[4],
                'image_path': row[5],
                'time': row[6],
                'location': row[7],
                'status': row[8],
                'created_at': row[9],
                'publisher': row[10]
            }
            items.append(item)

        # 获取总数（用于分页）
        count_sql = f"""
            SELECT COUNT(*) 
            FROM posts p
            WHERE {' AND '.join(where_conditions)}
        """
        cursor.execute(count_sql, params[:-2])  # 去掉LIMIT和OFFSET参数
        total_count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            "success": True,
            "data": {
                "items": items,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"查询失败: {str(e)}"}), 500


@app.route('/api/get_item_detail/<int:item_id>', methods=['GET'])
def get_item_detail(item_id):
    """获取单个失物招领信息的详细信息"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()

        sql = """
            SELECT 
                p.id,
                p.item_name,
                p.item_category,
                p.type,
                p.description,
                p.image_path,
                p.time,
                p.location,
                p.status,
                p.created_at,
                u.username as publisher,
                u.id as publisher_id
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        """

        cursor.execute(sql, (item_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return jsonify({"success": False, "message": "信息不存在"}), 404

        item = {
            'id': result[0],
            'item_name': result[1],
            'item_category': result[2],
            'type': result[3],
            'description': result[4],
            'image_path': result[5],
            'time': result[6],
            'location': result[7],
            'status': result[8],
            'created_at': result[9],
            'publisher': result[10],
            'publisher_id': result[11]
        }

        return jsonify({
            "success": True,
            "data": item
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"查询失败: {str(e)}"}), 500

@app.route('/data/uploads/<filename>')
def uploaded_file(filename):
    # 允许通过HTTP访问图片
    return send_from_directory(os.path.join(os.path.dirname(__file__), '../data/uploads'), filename)


@app.route('/api/edit_item', methods=['POST'])
def edit_item():
    """
    编辑物品信息接口。
    仅允许物品发布者本人编辑。
    可修改字段：type, item_name, item_category, description, image_path, time, location。
    前端需传递：id, 以及要修改的字段。
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "未登录，无法编辑"}), 401
    data = request.json
    item_id = data.get('id')
    # 校验参数
    if not item_id:
        return jsonify({"success": False, "message": "缺少物品ID"}), 400
    # 只允许修改这些字段
    fields = ['type', 'item_name', 'item_category', 'description', 'image_path', 'time', 'location']
    updates = {k: data[k] for k in fields if k in data}
    if not updates:
        return jsonify({"success": False, "message": "没有可修改的字段"}), 400
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        # 检查权限：只能编辑自己的物品
        cursor.execute("SELECT user_id FROM posts WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "message": "物品不存在"}), 404
        if row[0] != user_id:
            conn.close()
            return jsonify({"success": False, "message": "无权编辑他人发布的物品"}), 403
        # 构造SQL
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [item_id]
        sql = f"UPDATE posts SET {set_clause} WHERE id = ?"
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "编辑成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/delete_item', methods=['POST'])
def delete_item():
    """
    删除物品接口。
    仅允许物品发布者本人删除。
    前端需传递：id。
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "未登录，无法删除"}), 401
    data = request.json
    item_id = data.get('id')
    if not item_id:
        return jsonify({"success": False, "message": "缺少物品ID"}), 400
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        # 检查权限：只能删除自己的物品
        cursor.execute("SELECT user_id FROM posts WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "message": "物品不存在"}), 404
        if row[0] != user_id:
            conn.close()
            return jsonify({"success": False, "message": "无权删除他人发布的物品"}), 403
        # 删除数据
        cursor.execute("DELETE FROM posts WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/update_status', methods=['POST'])
def update_status():
    """
    修改物品状态接口。
    仅允许物品发布者本人修改。
    前端需传递：id。
    功能：active <-> found 状态切换。
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "未登录，无法修改状态"}), 401
    data = request.json
    item_id = data.get('id')
    if not item_id:
        return jsonify({"success": False, "message": "缺少物品ID"}), 400
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        # 检查权限：只能操作自己的物品
        cursor.execute("SELECT user_id, status FROM posts WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"success": False, "message": "物品不存在"}), 404
        if row[0] != user_id:
            conn.close()
            return jsonify({"success": False, "message": "无权操作他人发布的物品"}), 403
        # 状态切换
        current_status = row[1]
        new_status = 'found' if current_status == 'active' else 'active'
        cursor.execute("UPDATE posts SET status = ? WHERE id = ?", (new_status, item_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"状态已变更为{new_status}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)