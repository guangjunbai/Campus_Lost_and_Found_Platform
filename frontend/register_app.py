import sys
import requests
import os
from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from .config import get_api_url, get_timeout


class RegisterWindow(QDialog):#注册窗口
    def __init__(self, parent=None):#初始化注册窗口
        super().__init__(parent)#调用父类初始化
        self._setup_ui()#设置用户界面
        self._connect_signals()#连接信号和槽函数
        self._setup_window_properties()#设置窗口属性

    def _setup_ui(self):
        """设置用户界面"""
        loader = QUiLoader()#创建QUiLoader对象
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取项目根目录
        ui_path = os.path.join(project_root, "ui", "register.ui")#获取UI文件路径
        self.ui = loader.load(ui_path, self)#加载UI文件

    def _connect_signals(self):
        """连接信号和槽函数"""
        self.ui.register_pushButton.clicked.connect(self._handle_register)#连接注册按钮的点击事件到_handle_register函数
        self.ui.back_to_login_pushButton.clicked.connect(self._handle_back_to_login)#连接返回登录按钮的点击事件到_handle_back_to_login函数

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("用户注册")#设置窗口标题

    def _get_user_input(self) -> tuple[str, str, str]:
        """获取用户输入"""
        username = self.ui.username_lineEdit.text().strip()#获取用户名
        password = self.ui.password_lineEdit.text().strip()#获取密码
        confirm_password = self.ui.confirm_password_lineEdit.text().strip()#获取确认密码
        return username, password, confirm_password

    def _validate_input(self, username: str, password: str, confirm_password: str) -> bool:
        """验证用户输入"""
        if not username: #如果用户名为空
            QMessageBox.warning(self, "输入错误", "请输入用户名")#弹出提示框，提示用户输入用户名
            return False#返回False
        
        if len(username) < 3: #如果用户名长度小于3
            QMessageBox.warning(self, "输入错误", "用户名长度至少3个字符")#弹出提示框，提示用户用户名长度至少3个字符
            return False#返回False
        
        if not password: #如果密码为空
            QMessageBox.warning(self, "输入错误", "请输入密码")#弹出提示框，提示用户输入密码
            return False#返回False
        
        if len(password) < 6: #如果密码长度小于6
            QMessageBox.warning(self, "输入错误", "密码长度至少6个字符")#弹出提示框，提示用户密码长度至少6个字符
            return False#返回False
        
        if not confirm_password: #如果确认密码为空
            QMessageBox.warning(self, "输入错误", "请确认密码")#弹出提示框，提示用户确认密码
            return False#返回False
        
        if password != confirm_password: #如果密码和确认密码不一致
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")#弹出提示框，提示用户两次输入的密码不一致
            return False#返回False
        
        return True#返回True

    def _send_register_request(self, username: str, password: str) -> dict:
        """发送注册请求到服务器"""
        url = get_api_url("register")#注册请求的URL
        payload = {
            "username": username, #用户名
            "password": password #密码
        }
        try:
            response = requests.post(url, json=payload, timeout=get_timeout())
            return response.json()
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到服务器 {url}，请检查服务器是否启动")
        except requests.exceptions.Timeout:
            raise Exception(f"连接服务器超时，请检查网络连接")
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误: {e}")

    def _handle_register_response(self, result: dict):
        """处理注册响应"""
        if result.get("success"):
            QMessageBox.information(self, "注册成功", "用户注册成功！请返回登录页面登录。")#弹出提示框，提示用户注册成功
            self.accept()  # 注册成功关闭窗口
        else:
            QMessageBox.warning(self, "注册失败", result.get("message", "未知错误"))#如果注册失败，弹出提示框，提示用户注册失败

    def _handle_register(self):
        """注册按钮点击事件处理"""
        # 1. 获取用户输入
        username, password, confirm_password = self._get_user_input()
        
        # 2. 验证输入
        if not self._validate_input(username, password, confirm_password):
            return#返回
        
        # 3. 发送注册请求
        try:
            result = self._send_register_request(username, password)#发送注册请求
            self._handle_register_response(result)#处理注册响应
        except Exception as e:
            QMessageBox.critical(self, "网络错误", str(e))#如果网络请求错误，弹出提示框，提示用户网络错误

    def _handle_back_to_login(self):
        """返回登录按钮点击事件处理"""
        self.reject()  # 返回登录页面


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication#导入QApplication类
    
    app = QApplication(sys.argv)#创建QApplication对象
    window = RegisterWindow()#创建注册窗口
    window.show()#显示注册窗口
    sys.exit(app.exec()) #退出应用程序