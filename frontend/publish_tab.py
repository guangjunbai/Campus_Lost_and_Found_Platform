import os
import requests
from PySide6.QtWidgets import QMessageBox, QFileDialog, QPushButton, QLineEdit, QTextEdit, QComboBox, QDateTimeEdit
from .config import get_api_url, get_timeout

class PublishTab:
    def __init__(self, widget, session=None):
        self.ui = widget  # 直接使用主窗口传入的publish_tab widget
        self.session = session
        self.selected_image_path = None

        # 绑定所有需要用到的控件
        self.submit_pushButton = self.ui.findChild(QPushButton, "submit_pushButton")
        self.upload_image_pushButton = self.ui.findChild(QPushButton, "upload_image_pushButton")
        self.item_name_lineEdit = self.ui.findChild(QLineEdit, "item_name_lineEdit")
        self.item_category_comboBox = self.ui.findChild(QComboBox, "item_category_comboBox")
        self.item_type_comboBox = self.ui.findChild(QComboBox, "item_type_comboBox")
        self.description_textEdit = self.ui.findChild(QTextEdit, "description_textEdit")
        self.datetime_edit = self.ui.findChild(QDateTimeEdit, "datetime_edit")
        self.location_lineEdit = self.ui.findChild(QLineEdit, "location_lineEdit")

        self.setup_signals()

    def setup_signals(self):
        self.submit_pushButton.clicked.connect(self.handle_submit)
        self.upload_image_pushButton.clicked.connect(self.handle_upload_image)

    def handle_upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self.ui, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.selected_image_path = file_path
            self.upload_image_pushButton.setText("已选择")

    def handle_submit(self):
        # 获取表单数据
        item_name = self.item_name_lineEdit.text().strip()
        item_category = self.item_category_comboBox.currentText()
        item_type = self.item_type_comboBox.currentText()
        description = self.description_textEdit.toPlainText().strip()
        time = self.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        location = self.location_lineEdit.text().strip()

        # 校验
        if not item_name or not location:
            QMessageBox.warning(self.ui, "提示", "请填写所有必填项")
            return

        # 组装数据
        data = {
            "item_name": item_name,
            "item_category": item_category,
            "type": item_type,
            "description": description,
            "time": time,
            "location": location
        }

        files = None
        if self.selected_image_path:
            try:
                files = {'image': open(self.selected_image_path, 'rb')}
            except Exception as e:
                QMessageBox.warning(self.ui, "图片错误", f"图片无法读取: {e}")
                return

        # 发送请求
        try:
            if self.session:
                response = self.session.post(get_api_url("post"), data=data, files=files, timeout=get_timeout())
            else:
                response = requests.post(get_api_url("post"), data=data, files=files, timeout=get_timeout())
            result = response.json()
            if result.get("success"):
                QMessageBox.information(self.ui, "成功", "信息发布成功！")
                # 清空表单
                self.item_name_lineEdit.clear()
                self.description_textEdit.clear()
                self.location_lineEdit.clear()
                self.selected_image_path = None
                self.upload_image_pushButton.setText("上传图片")
            else:
                QMessageBox.warning(self.ui, "失败", result.get("message", "未知错误"))
        except Exception as e:
            QMessageBox.critical(self.ui, "网络错误", str(e))

    def get_widget(self):
        return self.ui.publish_tab  # 返回信息发布Tab的主控件