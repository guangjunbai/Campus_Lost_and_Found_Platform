#这个函数主要实现登录功能，包括登录请求、登录响应、登录成功后打开主窗口
#登录成功后，将session传递给主窗口，主窗口可以调用session中的方法，如获取用户信息
import sys
import os #用于获取项目根目录
import sqlite3 #用于数据库操作
import hashlib #用于密码加密
import requests #用于获取服务器响应
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtUiTools import QUiLoader
from .register_app import RegisterWindow #用于打开注册窗口
from .main_window import MainWindow #用于打开主窗口
from .config import get_api_url, get_timeout #导入配置函数

def hash_password(password: str, salt: str) -> str:
    """将密码和盐组合后哈希"""
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()


class LoginWindow(QDialog):
    def __init__(self):
        #初始化登录窗口
        super().__init__()
        self.session = requests.Session()  #创建Session对象，用于保持会话
        self._setup_ui() #设置用户界面
        self._connect_signals() #连接信号和槽函数
        self._setup_window_properties() #设置窗口属性   

    def _setup_ui(self):
        """设置用户界面"""
        loader = QUiLoader() #创建QUiLoader对象，用于加载UI文件
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #获取项目根目录
        ui_path = os.path.join(project_root, "ui", "login.ui") #获取UI文件路径
        self.ui = loader.load(ui_path, self) #加载UI文件

    def _connect_signals(self):
        """连接信号和槽函数"""
        self.ui.login_pushButton.clicked.connect(self._handle_login) #连接登录按钮的点击事件到_handle_login函数
        self.ui.register_pushButton.clicked.connect(self._handle_register) #连接注册按钮的点击事件到_handle_register函数

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle("简易登录系统") #设置窗口标题

    def _get_user_input(self) -> tuple[str, str]:
        """获取用户输入的用户名和密码"""
        username = self.ui.username_lineEdit.text().strip() #获取用户名
        password = self.ui.password_lineEdit.text().strip() #获取密码
        return username, password

    def _validate_input(self, username: str, password: str) -> bool:
        """验证用户输入"""
        if not username: #如果用户名为空
            QMessageBox.warning(self, "输入错误", "请输入用户名") #弹出提示框，提示用户输入用户名
            return False
        
        if not password: #如果密码为空
            QMessageBox.warning(self, "输入错误", "请输入密码") #弹出提示框，提示用户输入密码
            return False
        
        return True

    def _send_login_request(self, username: str, password: str) -> dict:
        """发送登录请求到服务器，使用 session 保持"""
        url = get_api_url("login") #从配置文件获取登录API的URL
        payload = {
            "username": username, #用户名
            "password": password #密码
        }
        
        try:
            # 使用配置的超时时间
            response = self.session.post(url, json=payload, timeout=get_timeout()) #发送登录请求
            return response.json() #返回服务器响应
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到服务器 {url}，请检查服务器是否启动") #如果无法连接到服务器，抛出异常
        except requests.exceptions.Timeout:
            raise Exception(f"连接服务器超时，请检查网络连接") #如果连接超时，抛出异常
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误: {e}") #如果网络请求错误，抛出异常

    def _handle_login_response(self, result: dict, username: str):
        """处理登录响应，登录成功后传递 session 给 MainWindow"""
        if result.get("success"):#如果登录成功
            QMessageBox.information(self, "登录成功", f"欢迎，{username}！") #弹出提示框，提示用户登录成功
            # 打开主窗口，传递 session
            self.main_window = MainWindow(username, session=self.session) #创建主窗口
            self.main_window.show() #显示主窗口
            self.accept()  # 登录成功关闭窗口
        else:
            QMessageBox.warning(self, "登录失败", result.get("message", "未知错误")) #弹出提示框，提示用户登录失败

    def _handle_login(self):
        """登录按钮点击事件处理"""
        # 1. 获取用户输入
        username, password = self._get_user_input() #获取用户输入
        
        # 2. 验证输入
        if not self._validate_input(username, password): #如果输入验证失败
            return #返回
        
        # 3. 发送登录请求
        try:
            result = self._send_login_request(username, password) #发送登录请求
            self._handle_login_response(result, username) #处理登录响应
        except Exception as e:
            QMessageBox.critical(self, "网络错误", str(e)) #如果网络请求错误，弹出提示框，提示用户网络错误

    def _handle_register(self):
        """注册按钮点击事件处理"""
        # 打开注册窗口
        register_window = RegisterWindow(self) #创建注册窗口
        result = register_window.exec() #执行注册窗口
        
        # 如果注册成功，可以选择自动填充用户名
        if result == QDialog.Accepted:
            # 注册成功，可以在这里添加一些逻辑
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv) #创建QApplication对象
    window = LoginWindow() #创建登录窗口
    window.show() #显示登录窗口
    sys.exit(app.exec())