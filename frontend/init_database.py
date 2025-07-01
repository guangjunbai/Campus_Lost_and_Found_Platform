import sqlite3
import os

DB_PATH = r"D:\SqliteDatabase\user.db"

def init_database():
    """初始化数据库，创建用户表"""
    # 确保数据库目录存在
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"创建数据库目录: {db_dir}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("数据库初始化成功！")
        print(f"数据库路径: {DB_PATH}")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")

if __name__ == "__main__":
    init_database() 