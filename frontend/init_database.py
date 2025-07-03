import sqlite3
import os

DB_PATH = r"D:\SqliteDatabase\user.db"

def init_database():
    """初始化数据库，创建用户表和失物招领信息表"""
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

        # 创建失物招领信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,  -- 'lost' 或 'found'
                item_name TEXT NOT NULL,
                item_category TEXT,
                description TEXT,
                image_path TEXT,
                time TEXT,
                location TEXT NOT NULL,
                status TEXT DEFAULT 'active',  -- 'active', 'resolved', 'expired'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # 创建索引以提高搜索性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posts_item_name ON posts (item_name)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posts_type ON posts (type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posts_category ON posts (item_category)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts (created_at)
        ''')
        
        conn.commit()
        conn.close()
        print("数据库初始化成功！")
        print(f"数据库路径: {DB_PATH}")
        print("已创建表: users, posts")
        print("已创建索引: idx_posts_item_name, idx_posts_type, idx_posts_category, idx_posts_created_at")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")

if __name__ == "__main__":
    init_database() 