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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改密码")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        self.old_password_edit = QLineEdit()
        self.old_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("原密码:", self.old_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("新密码:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("确认新密码:", self.confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_passwords(self):
        """获取输入的密码"""
        return (
            self.old_password_edit.text(),
            self.new_password_edit.text(),
            self.confirm_password_edit.text()
        )


class MainWindow(QMainWindow):
    def __init__(self, username: str, session=None):
        super().__init__()
        self.username = username
        self.login_time = datetime.now()
        self.session = session  # 新增，保存 session
        self._setup_ui()
        self._connect_signals()
        self._setup_window_properties()
        self._initialize_data()

    def _setup_ui(self):
        """设置用户界面"""
        loader = QUiLoader()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ui_path = os.path.join(project_root, "ui", "main_window.ui")
        self.ui = loader.load(ui_path, self)
        self.setCentralWidget(self.ui.centralwidget)
        self._add_tabs()

    def _add_tabs(self):
        # 用PublishTab替换信息发布Tab（假设索引1）
        self.publish_tab = PublishTab(self, session=self.session)
        self.ui.tabWidget.removeTab(1)
        self.ui.tabWidget.insertTab(1, self.publish_tab.get_widget(), "信息发布")

    def _connect_signals(self):
        """连接信号和槽函数"""
        # 用户管理标签页
        # self.ui.logout_pushButton.clicked.connect(self._handle_logout)
        
        # 系统设置标签页
        # self.ui.save_settings_pushButton.clicked.connect(self._handle_save_settings)
        
        # 菜单栏
        self.ui.action_logout.triggered.connect(self._handle_logout)
        # self.ui.action_exit.triggered.connect(self._handle_exit)
        # self.ui.action_about.triggered.connect(self._handle_about)

    def _setup_window_properties(self):
        """设置窗口属性"""
        self.setWindowTitle(f"主窗口 - {self.username}")
        self.resize(800, 600)

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