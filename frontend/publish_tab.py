import os
import requests
from PySide6.QtWidgets import QWidget, QMessageBox, QFileDialog
from PySide6.QtUiTools import QUiLoader
from .config import get_api_url, get_timeout

class PublishTab(QWidget):
    def __init__(self, parent=None, session=None):
        super().__init__(parent)
        # 加载UI
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))#获取项目根目录
        ui_path = os.path.join(project_root, "ui", "main_window.ui")#获取UI文件路径
        loader = QUiLoader()#创建QUiLoader对象
        self.ui = loader.load(ui_path, self)#加载UI文件
        self.selected_image_path = None
        self.session = session  # 新增，支持外部传入 session
        self.setup_signals()#设置信号和槽函数

    def setup_signals(self):
        self.ui.submit_pushButton.clicked.connect(self.handle_submit)#连接提交按钮的点击事件到handle_submit函数
        self.ui.upload_image_pushButton.clicked.connect(self.handle_upload_image)#连接上传图片按钮的点击事件到handle_upload_image函数

    def handle_upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")#打开文件对话框，选择图片
        if file_path:
            self.selected_image_path = file_path#设置选择的图片路径
            self.ui.upload_image_pushButton.setText("已选择")#设置上传图片按钮的文本为已选择

    def handle_submit(self):
        # 获取表单数据
        item_name = self.ui.item_name_lineEdit.text().strip()#获取物品名称
        item_category = self.ui.item_category_comboBox.currentText()#获取物品分类
        item_type = self.ui.item_type_comboBox.currentText()#获取物品类型
        description = self.ui.description_textEdit.toPlainText().strip()#获取物品描述
        time = self.ui.datetime_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")#获取物品时间
        location = self.ui.location_lineEdit.text().strip()#获取物品地点

        # 校验
        if not item_name or not location:
            QMessageBox.warning(self, "提示", "请填写所有必填项")#如果物品名称或地点为空，弹出提示框，提示用户填写所有必填项
            return#返回

        # 组装数据
        data = {
            "item_name": item_name, #物品名称
            "item_category": item_category, #物品分类
            "type": item_type, #物品类型
            "description": description, #物品描述
            "time": time, #物品时间
            "location": location #物品地点
        }

        files = None#初始化文件列表
        if self.selected_image_path:
            try:
                files = {'image': open(self.selected_image_path, 'rb')}#打开选择的图片
            except Exception as e:
                QMessageBox.warning(self, "图片错误", f"图片无法读取: {e}")#如果图片无法读取，弹出提示框，提示用户图片无法读取
                return#返回

        # 发送请求
        try:
            if self.session:
                response = self.session.post(get_api_url("post"), data=data, files=files, timeout=get_timeout())#发送请求
            else:
                response = requests.post(get_api_url("post"), data=data, files=files, timeout=get_timeout())#发送请求
            result = response.json()#获取服务器响应
            if result.get("success"):#如果服务器响应成功
                QMessageBox.information(self, "成功", "信息发布成功！")#弹出提示框，提示用户信息发布成功
                # 清空表单
                self.ui.item_name_lineEdit.clear()#清空物品名称
                self.ui.description_textEdit.clear()#清空物品描述
                self.ui.location_lineEdit.clear()#清空物品地点
                self.selected_image_path = None
                self.ui.upload_image_pushButton.setText("上传图片")#设置上传图片按钮的文本为上传图片
            else:
                QMessageBox.warning(self, "失败", result.get("message", "未知错误"))#如果服务器响应失败，弹出提示框，提示用户信息发布失败
        except Exception as e:
            QMessageBox.critical(self, "网络错误", str(e))#如果网络请求错误，弹出提示框，提示用户网络错误

    def get_widget(self):
        return self.ui.publish_tab  # 返回信息发布Tab的主控件