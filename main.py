import sys
from PySide6.QtWidgets import QApplication
from frontend.login_app import LoginWindow


def main():
    """主程序入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("简易登录系统")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MyCompany")
    
    # 创建并显示登录窗口
    login_window = LoginWindow()
    login_window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 