import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QPushButton, QInputDialog, QDialog, QFormLayout, QComboBox, QLineEdit, QDialogButtonBox, QTextEdit, QDateTimeEdit
)
from PySide6.QtCore import Qt, QDateTime
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
            "description": self.current_items[row].get("description", ""),
            "image_path": self.current_items[row].get("image_path", ""),
            "time": self.table.item(row, 5).text(),
            "location": self.table.item(row, 4).text(),
        }
        dialog = EditItemDialog(item_data, self)
        if dialog.exec() == QDialog.Accepted:
            new_data = dialog.get_data()
            item_data.update(new_data)
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

class EditItemDialog(QDialog):
    """多字段编辑对话框"""
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑物品信息")
        self.item_data = item_data
        layout = QFormLayout(self)
        # 物品名称
        self.name_edit = QLineEdit(item_data["item_name"])
        layout.addRow("物品名称", self.name_edit)
        # 类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["失物信息", "招领信息"])
        self.type_combo.setCurrentText(item_data["type"])
        layout.addRow("类型", self.type_combo)
        # 分类
        self.category_combo = QComboBox()
        self.category_combo.addItems(["书本", "电子产品", "证件卡片", "衣物饰品", "其他"])
        self.category_combo.setCurrentText(item_data["item_category"])
        layout.addRow("分类", self.category_combo)
        # 描述
        self.desc_edit = QTextEdit(item_data.get("description", ""))
        layout.addRow("描述", self.desc_edit)
        # 时间
        self.time_edit = QDateTimeEdit()
        try:
            dt = QDateTime.fromString(item_data["time"], "yyyy-MM-dd HH:mm:ss")
            if dt.isValid():
                self.time_edit.setDateTime(dt)
        except:
            pass
        layout.addRow("时间", self.time_edit)
        # 地点
        self.location_edit = QLineEdit(item_data["location"])
        layout.addRow("地点", self.location_edit)
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    def get_data(self):
        return {
            "item_name": self.name_edit.text(),
            "type": self.type_combo.currentText(),
            "item_category": self.category_combo.currentText(),
            "description": self.desc_edit.toPlainText(),
            "time": self.time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "location": self.location_edit.text(),
        } 