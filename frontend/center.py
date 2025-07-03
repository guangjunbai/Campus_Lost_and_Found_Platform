import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QPushButton, QInputDialog
)
from PySide6.QtCore import Qt
from .config import get_api_url, get_timeout

class CenterTab(QWidget):
    """个人中心-信息展示，仅展示当前用户发布的物品（按用户名筛选）"""
    def __init__(self, username, edit_btn=None, delete_btn=None, status_btn=None, session=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.session = session  # 用于保持登录态
        self.current_items = []
        self.setup_ui()
        self.load_my_items()
        # 绑定外部按钮
        if edit_btn:
            edit_btn.clicked.connect(self.handle_edit_post)
        if delete_btn:
            delete_btn.clicked.connect(self.handle_delete_post)
        if status_btn:
            status_btn.clicked.connect(self.handle_mark_found)

    def setup_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("我的发布：0 条")
        layout.addWidget(self.status_label)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "物品名称", "类型", "分类", "地点", "时间", "状态"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_my_items)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)

    def load_my_items(self):
        try:
            response = requests.get(get_api_url("get_lost_items"), timeout=get_timeout())
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    all_items = result["data"]["items"]
                    # 用用户名筛选
                    my_items = [item for item in all_items if item.get("publisher") == self.username]
                    self.current_items = my_items
                    self.update_table()
                    self.status_label.setText(f"我的发布：{len(my_items)} 条")
                else:
                    QMessageBox.warning(self, "加载失败", result.get("message", "未知错误"))
            else:
                QMessageBox.warning(self, "网络错误", f"HTTP错误: {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "网络错误", str(e))

    def update_table(self):
        self.table.setRowCount(len(self.current_items))
        for row, item in enumerate(self.current_items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get('id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(item.get('item_name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(item.get('type', '')))
            self.table.setItem(row, 3, QTableWidgetItem(item.get('item_category', '')))
            self.table.setItem(row, 4, QTableWidgetItem(item.get('location', '')))
            self.table.setItem(row, 5, QTableWidgetItem(item.get('time', '')))
            self.table.setItem(row, 6, QTableWidgetItem(item.get('status', '')))

    def get_selected_item_id(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "提示", "请先选中一条记录")
            return None
        row = selected[0].row()
        item_id = self.table.item(row, 0).text()
        return item_id

    def handle_delete_post(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        reply = QMessageBox.question(self, "确认删除", "确定要删除该条信息吗？", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        import requests
        url = get_api_url("delete_item")
        try:
            resp = requests.post(url, json={"id": int(item_id)}, cookies=self.session.cookies if self.session else None)
            result = resp.json()
            if result.get("success"):
                QMessageBox.information(self, "成功", "删除成功")
                self.load_my_items()
            else:
                QMessageBox.warning(self, "失败", result.get("message", "删除失败"))
        except Exception as e:
            QMessageBox.warning(self, "网络错误", str(e))

    def handle_mark_found(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        import requests
        url = get_api_url("update_status")
        try:
            resp = requests.post(url, json={"id": int(item_id)}, cookies=self.session.cookies if self.session else None)
            result = resp.json()
            if result.get("success"):
                QMessageBox.information(self, "成功", result.get("message", "状态已变更"))
                self.load_my_items()
            else:
                QMessageBox.warning(self, "失败", result.get("message", "操作失败"))
        except Exception as e:
            QMessageBox.warning(self, "网络错误", str(e))

    def handle_edit_post(self):
        item_id = self.get_selected_item_id()
        if not item_id:
            return
        row = self.table.currentRow()
        item_data = {
            "id": int(item_id),
            "type": self.table.item(row, 2).text(),
            "item_name": self.table.item(row, 1).text(),
            "item_category": self.table.item(row, 3).text(),
            "description": "",  # 可扩展：弹窗里加描述输入框
            "image_path": "",   # 可扩展：弹窗里加图片上传
            "time": self.table.item(row, 5).text(),
            "location": self.table.item(row, 4).text(),
        }
        # 弹出对话框让用户编辑（这里只做简单输入框示例）
        new_name, ok = QInputDialog.getText(self, "编辑物品名称", "物品名称：", text=item_data["item_name"])
        if not ok:
            return
        item_data["item_name"] = new_name
        import requests
        url = get_api_url("edit_item")
        try:
            resp = requests.post(url, json=item_data, cookies=self.session.cookies if self.session else None)
            result = resp.json()
            if result.get("success"):
                QMessageBox.information(self, "成功", "编辑成功")
                self.load_my_items()
            else:
                QMessageBox.warning(self, "失败", result.get("message", "编辑失败"))
        except Exception as e:
            QMessageBox.warning(self, "网络错误", str(e)) 