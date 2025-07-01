import sys
import requests
import os
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader


class RegisterWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        self._setup_window_properties()

    def _setup_ui(self):
        """设置用户界面"""
        loader = QUiLoader()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ui_path = os.path.join(project_root, "ui", "register.ui")
        self.ui = loader.load(ui_path, self)

    def _connect_signals(self):
        """连接信号和槽函数"""
        self.ui.register_pushButton.clicked.connect(self._handle_register)
        self.ui.back_to_login_pushButton.clicked.connect(self._handle_back_to_login)

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("用户注册")

    def _get_user_input(self) -> tuple[str, str, str]:
        """获取用户输入"""
        username = self.ui.username_lineEdit.text().strip()
        password = self.ui.password_lineEdit.text().strip()
        confirm_password = self.ui.confirm_password_lineEdit.text().strip()
        return username, password, confirm_password

    def _validate_input(self, username: str, password: str, confirm_password: str) -> bool:
        """验证用户输入"""
        if not username:
            QMessageBox.warning(self, "输入错误", "请输入用户名")
            return False
        
        if len(username) < 3:
            QMessageBox.warning(self, "输入错误", "用户名长度至少3个字符")
            return False
        
        if not password:
            QMessageBox.warning(self, "输入错误", "请输入密码")
            return False
        
        if len(password) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度至少6个字符")
            return False
        
        if not confirm_password:
            QMessageBox.warning(self, "输入错误", "请确认密码")
            return False
        
        if password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return False
        
        return True

    def _send_register_request(self, username: str, password: str) -> dict:
        """发送注册请求到服务器"""
        url = "http://127.0.0.1:5000/api/register"
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

    def _handle_register_response(self, result: dict):
        """处理注册响应"""
        if result.get("success"):
            QMessageBox.information(self, "注册成功", "用户注册成功！请返回登录页面登录。")
            self.accept()  # 注册成功关闭窗口
        else:
            QMessageBox.warning(self, "注册失败", result.get("message", "未知错误"))

    def _handle_register(self):
        """注册按钮点击事件处理"""
        # 1. 获取用户输入
        username, password, confirm_password = self._get_user_input()
        
        # 2. 验证输入
        if not self._validate_input(username, password, confirm_password):
            return
        
        # 3. 发送注册请求
        try:
            result = self._send_register_request(username, password)
            self._handle_register_response(result)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", str(e))

    def _handle_back_to_login(self):
        """返回登录按钮点击事件处理"""
        self.reject()  # 返回登录页面


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec()) 