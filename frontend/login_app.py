import sys
import sqlite3
import hashlib
import requests
import os
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from .register_app import RegisterWindow
from .main_window import MainWindow


def hash_password(password: str, salt: str) -> str:
    """将密码和盐组合后哈希"""
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
        self._setup_window_properties()

    def _setup_ui(self):
        """设置用户界面"""
        loader = QUiLoader()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ui_path = os.path.join(project_root, "ui", "login.ui")
        self.ui = loader.load(ui_path, self)

    def _connect_signals(self):
        """连接信号和槽函数"""
        self.ui.login_pushButton.clicked.connect(self._handle_login)
        self.ui.register_pushButton.clicked.connect(self._handle_register)

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("简易登录系统")

    def _get_user_input(self) -> tuple[str, str]:
        """获取用户输入的用户名和密码"""
        username = self.ui.username_lineEdit.text().strip()
        password = self.ui.password_lineEdit.text().strip()
        return username, password

    def _validate_input(self, username: str, password: str) -> bool:
        """验证用户输入"""
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            return False
        
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            return False
        
        return True

    def _send_login_request(self, username: str, password: str) -> dict:
        """发送登录请求到服务器"""
        url = "http://127.0.0.1:5000/api/login"
        payload = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.json()
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到服务器，请检查服务器是否启动")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误: {e}")

    def _handle_login_response(self, result: dict, username: str):
        """处理登录响应"""
        if result.get("success"):
            QMessageBox.information(self, "登录成功", f"欢迎，{username}！")
            
            # 打开主窗口
            self.main_window = MainWindow(username)
            self.main_window.show()
            
            self.accept()  # 登录成功关闭窗口
        else:
            QMessageBox.warning(self, "登录失败", result.get("message", "未知错误"))

    def _handle_login(self):
        """登录按钮点击事件处理"""
        # 1. 获取用户输入
        username, password = self._get_user_input()
        
        # 2. 验证输入
        if not self._validate_input(username, password):
            return
        
        # 3. 发送登录请求
        try:
            result = self._send_login_request(username, password)
            self._handle_login_response(result, username)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", str(e))

    def _handle_register(self):
        """注册按钮点击事件处理"""
        # 打开注册窗口
        register_window = RegisterWindow(self)
        result = register_window.exec()
        
        # 如果注册成功，可以选择自动填充用户名
        if result == QDialog.Accepted:
            # 注册成功，可以在这里添加一些逻辑
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())