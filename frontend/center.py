import sys
import os
import tempfile
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QAbstractItemView, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from datetime import datetime

class EditItemDialog(QDialog):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑物品信息")
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["lost", "found"])
        self.type_combo.setCurrentText(item_data.get('type', 'lost'))
        self.item_name_edit = QLineEdit(item_data.get('item_name', ''))
        self.item_category_edit = QLineEdit(item_data.get('item_category', ''))
        self.description_edit = QLineEdit(item_data.get('description', ''))
        self.location_edit = QLineEdit(item_data.get('location', ''))
        self.time_edit = QLineEdit(item_data.get('time', ''))
        self.image_path_edit = QLineEdit(item_data.get('image_path', ''))
        form_layout.addRow("类型:", self.type_combo)
        form_layout.addRow("物品名称:", self.item_name_edit)
        form_layout.addRow("物品分类:", self.item_category_edit)
        form_layout.addRow("描述:", self.description_edit)
        form_layout.addRow("地点:", self.location_edit)
        form_layout.addRow("时间:", self.time_edit)
        form_layout.addRow("图片路径:", self.image_path_edit)
        layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return {
            'type': self.type_combo.currentText(),
            'item_name': self.item_name_edit.text(),
            'item_category': self.item_category_edit.text(),
            'description': self.description_edit.text(),
            'location': self.location_edit.text(),
            'time': self.time_edit.text(),
            'image_path': self.image_path_edit.text()
        }

class MyItemsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("我发布的物品")
        self.setMinimumSize(900, 500)
        main_layout = QVBoxLayout()
        title_layout = QHBoxLayout()
        title_label = QLabel("我发布的物品")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.load_items)
        title_layout.addWidget(self.refresh_button)
        main_layout.addLayout(title_layout)
        self.status_label = QLabel("正在加载数据...")
        main_layout.addWidget(self.status_label)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "名称", "分类", "状态", "时间", "图片", "操作"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        QTimer.singleShot(100, self.load_items)

    def load_items(self):
        self.status_label.setText("正在加载数据...")
        self.refresh_button.setEnabled(False)
        try:
            response = requests.get("http://localhost:5000/api/my_posts")
            if response.status_code == 200 and response.json()["success"]:
                items = response.json()["data"]
                self.populate_table(items)
                self.status_label.setText(f"加载成功，共 {len(items)} 条")
            else:
                self.status_label.setText("加载失败")
        except Exception as e:
            self.status_label.setText(f"加载失败: {str(e)}")
        finally:
            self.refresh_button.setEnabled(True)

    def populate_table(self, items):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["item_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("item_category", "")))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("status", "")))
            created_at = item.get("created_at", "")
            self.table.setItem(row, 4, QTableWidgetItem(created_at))
            img_label = QLabel("无图片")
            if item.get("image_path"):
                try:
                    image_url = f"http://localhost:5000/uploads/{os.path.basename(item['image_path'])}"
                    resp = requests.get(image_url)
                    if resp.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                            tmp_file.write(resp.content)
                            tmp_path = tmp_file.name
                        pixmap = QPixmap(tmp_path)
                        img_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio))
                except:
                    img_label.setText("图片加载失败")
            self.table.setCellWidget(row, 5, img_label)
            # 操作按钮
            op_widget = QWidget()
            op_layout = QHBoxLayout()
            edit_btn = QPushButton("编辑")
            edit_btn.setProperty("item_id", item["id"])
            edit_btn.setProperty("item_data", item)
            edit_btn.clicked.connect(self.handle_edit)
            del_btn = QPushButton("删除")
            del_btn.setProperty("item_id", item["id"])
            del_btn.setProperty("item_name", item["item_name"])
            del_btn.clicked.connect(self.handle_delete)
            mark_btn = QPushButton("标记为已找回")
            mark_btn.setProperty("item_id", item["id"])
            mark_btn.clicked.connect(self.handle_mark_found)
            op_layout.addWidget(edit_btn)
            op_layout.addWidget(del_btn)
            op_layout.addWidget(mark_btn)
            op_widget.setLayout(op_layout)
            self.table.setCellWidget(row, 6, op_widget)

    def handle_edit(self):
        btn = self.sender()
        item_id = btn.property("item_id")
        item_data = btn.property("item_data")
        dialog = EditItemDialog(item_data, self)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            new_data["item_id"] = item_id
            try:
                response = requests.post(
                    "http://localhost:5000/api/edit_item",
                    json=new_data
                )
                if response.status_code == 200 and response.json()["success"]:
                    QMessageBox.information(self, "成功", "物品信息更新成功")
                    self.load_items()
                else:
                    QMessageBox.warning(self, "错误", "更新失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def handle_delete(self):
        btn = self.sender()
        item_id = btn.property("item_id")
        item_name = btn.property("item_name")
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除物品 '{item_name}' 吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                response = requests.post(
                    "http://localhost:5000/api/delete_item",
                    json={"item_id": item_id}
                )
                if response.status_code == 200 and response.json()["success"]:
                    QMessageBox.information(self, "成功", "物品删除成功")
                    self.load_items()
                else:
                    QMessageBox.warning(self, "错误", "删除失败")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def handle_mark_found(self):
        btn = self.sender()
        item_id = btn.property("item_id")
        try:
            response = requests.post(
                "http://localhost:5000/api/update_item",
                json={"item_id": item_id, "status": "found"}
            )
            if response.status_code == 200 and response.json()["success"]:
                QMessageBox.information(self, "成功", "已标记为已找回")
                self.load_items()
            else:
                QMessageBox.warning(self, "错误", "操作失败")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

def main():
    app = QApplication(sys.argv)
    window = MyItemsPage()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 