import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QInputDialog, QDialog, QVBoxLayout, 
    QFormLayout, QLineEdit, QPushButton, QDialogButtonBox
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt
from .publish_tab import PublishTab


class ChangePasswordDialog(QDialog):
    """修改密码对话框"""
    def __init__(self, parent=None):#初始化对话框
        super().__init__(parent)#调用父类初始化
        self.setWindowTitle("修改密码")#设置窗口标题
        self.setModal(True)#设置对话框为模态
        self.setup_ui()#设置对话框界面
        
    def setup_ui(self):#设置对话框界面
        layout = QVBoxLayout()#创建垂直布局
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        self.old_password_edit = QLineEdit()#创建原密码输入框
        self.old_password_edit.setEchoMode(QLineEdit.Password)#设置原密码输入框为密码模式
        form_layout.addRow("原密码:", self.old_password_edit)#添加原密码标签和输入框
        
        self.new_password_edit = QLineEdit()#创建新密码输入框
        self.new_password_edit.setEchoMode(QLineEdit.Password)#设置新密码输入框为密码模式
        form_layout.addRow("新密码:", self.new_password_edit)#添加新密码标签和输入框
        
        self.confirm_password_edit = QLineEdit()#创建确认新密码输入框
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)#设置确认新密码输入框为密码模式
        form_layout.addRow("确认新密码:", self.confirm_password_edit)#添加确认新密码标签和输入框
        
        layout.addLayout(form_layout)#添加表单布局
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)#连接确认按钮的点击事件到accept函数
        button_box.rejected.connect(self.reject)#连接取消按钮的点击事件到reject函数
        layout.addWidget(button_box)
        
        self.setLayout(layout)#设置对话框布局
    
    def get_passwords(self):
        """获取输入的密码"""
        return (
            self.old_password_edit.text(),#获取原密码
            self.new_password_edit.text(),#获取新密码
            self.confirm_password_edit.text()#获取确认新密码
        )


class MainWindow(QMainWindow):
    def __init__(self, username: str, session=None):#初始化主窗口
        super().__init__()#调用父类初始化
        self.username = username#设置用户名
        self.login_time = datetime.now()#设置登录时间
        self.session = session  # 新增，保存 session
        self._setup_ui()#设置用户界面
        self._connect_signals()#连接信号和槽函数
        self._setup_window_properties()#设置窗口属性
        self._initialize_data()#初始化数据

    def _setup_ui(self):
        """设置用户界面"""
        loader = QUiLoader()#创建QUiLoader对象
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取项目根目录
        ui_path = os.path.join(project_root, "ui", "main_window.ui")#获取UI文件路径
        self.ui = loader.load(ui_path, self)#加载UI文件
        self.setCentralWidget(self.ui.centralwidget)#设置中央窗口
        self._add_tabs()#添加标签页

    def _add_tabs(self):
        # 直接将UI里的publish_tab widget传递给自定义逻辑类
        self.publish_tab = PublishTab(self.ui.publish_tab, session=self.session)

    def _connect_signals(self):
        """连接信号和槽函数"""
        # 用户管理标签页
        # self.ui.logout_pushButton.clicked.connect(self._handle_logout)
        
        # 系统设置标签页
        # self.ui.save_settings_pushButton.clicked.connect(self._handle_save_settings)
        
        # 菜单栏
        self.ui.action_logout.triggered.connect(self._handle_logout)#连接退出登录按钮的点击事件到_handle_logout函数
        # self.ui.action_exit.triggered.connect(self._handle_exit)
        # self.ui.action_about.triggered.connect(self._handle_about)

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle(f"主窗口 - {self.username}")#设置窗口标题
        self.resize(800, 600)#设置窗口大小

    def _initialize_data(self):
        """初始化数据"""
        # 设置用户信息（已移除current_username_lineEdit和login_time_lineEdit相关代码）
        # self.ui.current_username_lineEdit.setText(self.username)
        # self.ui.login_time_lineEdit.setText(self.login_time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # 设置欢迎信息
        welcome_text = f"欢迎，{self.username}！\n登录时间：{self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"
        # self.ui.welcome_label.setText(welcome_text)  # 如果有欢迎标签可以恢复
        
        # 设置状态栏信息
        self.ui.statusbar.showMessage(f"用户：{self.username} | 登录时间：{self.login_time.strftime('%H:%M:%S')}")

    def _handle_logout(self):
        """处理退出登录"""
        reply = QMessageBox.question(
            self, "确认退出", "确定要退出登录吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
            # 这里可以发送信号通知主程序返回登录界面

    def _handle_exit(self):
        """处理退出程序"""
        reply = QMessageBox.question(
            self, "确认退出", "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()

    def _handle_about(self):
        """处理关于对话框"""
        QMessageBox.about(
            self, "关于",
            "简易登录系统 v1.0\n\n"
            "这是一个使用 PySide6 和 Flask 开发的登录系统。\n"
            "支持用户注册、登录和基本的管理功能。"
        )

    def closeEvent(self, event):
        """窗口关闭事件"""
        reply = QMessageBox.question(
            self, "确认退出", "确定要退出程序吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow("测试用户")
    window.show()
    sys.exit(app.exec()) 