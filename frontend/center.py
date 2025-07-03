import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QPushButton
)
from PySide6.QtCore import Qt
from .config import get_api_url, get_timeout

class CenterTab(QWidget):
    """个人中心-信息展示，仅展示当前用户发布的物品（按用户名筛选）"""
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.current_items = []
        self.setup_ui()
        self.load_my_items()

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