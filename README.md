# 简易登录系统

这是一个使用 PySide6 和 Flask 开发的桌面登录系统，支持用户注册、登录和基本的管理功能。

## 功能特性

### 用户功能
- ✅ 用户注册
- ✅ 用户登录
- ✅ 修改密码
- ✅ 退出登录

### 系统功能
- ✅ 多标签页界面
- ✅ 用户信息管理
- ✅ 系统设置
- ✅ 菜单栏和状态栏

## 项目结构

```
pycharmTest/
├── main.py                 # 主程序入口
├── login_app.py           # 登录窗口
├── register_app.py        # 注册窗口
├── main_window.py         # 主窗口
├── login.ui              # 登录界面UI
├── register.ui           # 注册界面UI
├── main_window.ui        # 主窗口UI
├── server/
│   └── flask_app.py      # Flask后端API
├── init_database.py      # 数据库初始化脚本
└── README.md             # 项目说明
```

## 安装和运行

### 1. 安装依赖

```bash
pip install PySide6 flask requests
```

### 2. 初始化数据库

```bash
python init_database.py
```

### 3. 启动后端服务器

```bash
cd server
python flask_app.py
```

### 4. 启动前端应用程序

```bash
python main.py
```

## 使用说明

### 注册新用户
1. 点击登录界面的"注册"按钮
2. 填写用户名（至少3个字符）
3. 填写密码（至少6个字符）
4. 确认密码
5. 点击"注册"按钮

### 用户登录
1. 在登录界面输入用户名和密码
2. 点击"登录"按钮
3. 登录成功后会自动跳转到主窗口

### 主窗口功能
- **首页**：显示欢迎信息和系统公告
- **用户管理**：查看用户信息、修改密码、退出登录
- **系统设置**：设置主题和字体大小

## 技术栈

- **前端**：PySide6 (Qt for Python)
- **后端**：Flask (Python Web框架)
- **数据库**：SQLite
- **密码加密**：SHA256 + 盐值

## 开发说明

### 代码结构
代码采用模块化设计，每个功能都有独立的类和文件：
- 登录功能：`LoginWindow` 类
- 注册功能：`RegisterWindow` 类
- 主窗口：`MainWindow` 类
- 后端API：Flask路由

### 数据库设计
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 扩展功能

可以继续添加的功能：
- [ ] 用户头像上传
- [ ] 记住密码功能
- [ ] 自动登录
- [ ] 用户权限管理
- [ ] 日志记录
- [ ] 数据备份和恢复

## 注意事项

1. 确保数据库路径正确（默认：`D:\SqliteDatabase\user.db`）
2. 启动应用程序前需要先启动Flask后端服务器
3. 密码使用SHA256+盐值加密存储，确保安全性

## 许可证

MIT License 