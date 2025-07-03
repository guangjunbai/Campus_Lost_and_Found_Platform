import os
import requests
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QComboBox,
    QMessageBox, QDialog, QFormLayout, QTextEdit, QScrollArea,
    QFrame, QSplitter, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from .config import get_api_url, get_timeout


class ItemDetailDialog(QDialog):
    """失物招领信息详情对话框"""

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("详细信息")
        self.setModal(True)
        self.resize(600, 500)

        layout = QVBoxLayout()

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # 标题
        title_label = QLabel(f"【{self.item_data['type']}】{self.item_data['item_name']}")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title_label)

        # 图片显示
        if self.item_data.get('image_path'):
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setMaximumHeight(200)

            # 拼接HTTP图片URL
            image_path = self.item_data['image_path']
            image_url = f"http://localhost:5000/{image_path}"
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        image_label.setPixmap(pixmap)
                    else:
                        image_label.setText("图片加载失败")
                else:
                    image_label.setText("图片加载失败")
            except Exception as e:
                image_label.setText("图片加载异常")

            scroll_layout.addWidget(image_label)

        # 信息表单
        form_layout = QFormLayout()

        # 基本信息
        form_layout.addRow("分类:", QLabel(self.item_data.get('item_category', '未知')))
        form_layout.addRow("类型:", QLabel(self.item_data.get('type', '未知')))
        form_layout.addRow("时间:", QLabel(self.item_data.get('time', '未知')))
        form_layout.addRow("地点:", QLabel(self.item_data.get('location', '未知')))
        form_layout.addRow("发布者:", QLabel(self.item_data.get('publisher', '未知')))
        form_layout.addRow("状态:", QLabel(self.item_data.get('status', '未知')))
        form_layout.addRow("发布时间:", QLabel(self.item_data.get('created_at', '未知')))

        scroll_layout.addLayout(form_layout)

        # 描述信息
        if self.item_data.get('description'):
            desc_label = QLabel("详细描述:")
            desc_label.setFont(QFont("Arial", 10, QFont.Bold))
            scroll_layout.addWidget(desc_label)

            desc_text = QTextEdit()
            desc_text.setPlainText(self.item_data['description'])
            desc_text.setReadOnly(True)
            desc_text.setMaximumHeight(100)
            scroll_layout.addWidget(desc_text)

        # 添加弹性空间
        scroll_layout.addStretch()

        # 设置滚动区域
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)


class SearchWorker(QThread):
    """搜索工作线程，避免界面卡顿"""
    search_finished = Signal(dict)
    search_error = Signal(str)

    def __init__(self, keyword="", item_type="", category="", limit=50, offset=0):
        super().__init__()
        self.keyword = keyword
        self.item_type = item_type
        self.category = category
        self.limit = limit
        self.offset = offset

    def run(self):
        try:
            params = {
                'keyword': self.keyword,
                'type': self.item_type,
                'category': self.category,
                'limit': self.limit,
                'offset': self.offset
            }

            # 移除空参数
            params = {k: v for k, v in params.items() if v}

            response = requests.get(
                get_api_url("get_lost_items"),
                params=params,
                timeout=get_timeout()
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.search_finished.emit(result["data"])
                else:
                    self.search_error.emit(result.get("message", "搜索失败"))
            else:
                self.search_error.emit(f"HTTP错误: {response.status_code}")

        except Exception as e:
            self.search_error.emit(f"网络错误: {str(e)}")


class SearchTab(QWidget):
    """搜索功能标签页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_worker = None
        self.current_items = []
        self.setup_ui()
        self.setup_signals()
        self.load_initial_data()

    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout()

        # 搜索区域
        search_frame = QFrame()
        search_frame.setFrameStyle(QFrame.StyledPanel)
        search_layout = QVBoxLayout(search_frame)

        # 搜索输入行
        search_input_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键字搜索（物品名称、描述、地点）")
        self.search_input.setMinimumHeight(35)
        search_input_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.setMinimumHeight(35)
        search_input_layout.addWidget(self.search_btn)

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setMinimumHeight(35)
        search_input_layout.addWidget(self.clear_btn)

        search_layout.addLayout(search_input_layout)

        # 筛选条件行
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("全部", "")
        self.type_combo.addItem("失物", "lost")
        self.type_combo.addItem("招领", "found")
        filter_layout.addWidget(self.type_combo)

        filter_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部", "")
        self.category_combo.addItem("电子产品", "电子产品")
        self.category_combo.addItem("书籍资料", "书籍资料")
        self.category_combo.addItem("证件卡片", "证件卡片")
        self.category_combo.addItem("衣物饰品", "衣物饰品")
        self.category_combo.addItem("其他", "其他")
        filter_layout.addWidget(self.category_combo)

        filter_layout.addStretch()

        # 统计信息
        self.status_label = QLabel("共找到 0 条记录")
        filter_layout.addWidget(self.status_label)

        search_layout.addLayout(filter_layout)
        layout.addWidget(search_frame)

        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(7)
        self.result_table.setHorizontalHeaderLabels([
            "ID", "物品名称", "类型", "分类", "地点", "时间", "发布者"
        ])

        # 设置表格属性
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSortingEnabled(True)

        # 设置列宽
        header = self.result_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 物品名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 分类
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 地点
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 时间
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 发布者

        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def setup_signals(self):
        """连接信号和槽函数"""
        self.search_btn.clicked.connect(self.perform_search)
        self.clear_btn.clicked.connect(self.clear_search)
        self.search_input.returnPressed.connect(self.perform_search)
        self.type_combo.currentTextChanged.connect(self.on_filter_changed)
        self.category_combo.currentTextChanged.connect(self.on_filter_changed)
        self.result_table.itemDoubleClicked.connect(self.show_item_detail)

        # 设置搜索防抖
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_input.textChanged.connect(self.on_search_text_changed)

    def on_search_text_changed(self):
        """搜索文本变化时启动防抖定时器"""
        self.search_timer.start(500)  # 500ms防抖

    def on_filter_changed(self):
        """筛选条件变化时自动搜索"""
        self.perform_search()

    def load_initial_data(self):
        """加载初始数据"""
        self.perform_search()

    def perform_search(self):
        """执行搜索"""
        keyword = self.search_input.text().strip()
        item_type = self.type_combo.currentData()
        category = self.category_combo.currentData()

        # 停止之前的搜索线程
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()

        # 创建新的搜索线程
        self.search_worker = SearchWorker(keyword, item_type, category)
        self.search_worker.search_finished.connect(self.on_search_finished)
        self.search_worker.search_error.connect(self.on_search_error)
        self.search_worker.start()

        # 显示加载状态
        self.search_btn.setText("搜索中...")
        self.search_btn.setEnabled(False)

    def on_search_finished(self, data):
        """搜索完成处理"""
        self.search_btn.setText("搜索")
        self.search_btn.setEnabled(True)

        self.current_items = data.get('items', [])
        self.update_table()

        # 更新状态信息
        total = data.get('total', 0)
        self.status_label.setText(f"共找到 {total} 条记录")

    def on_search_error(self, error_msg):
        """搜索错误处理"""
        self.search_btn.setText("搜索")
        self.search_btn.setEnabled(True)
        QMessageBox.warning(self, "搜索错误", error_msg)

    def update_table(self):
        """更新表格数据"""
        self.result_table.setRowCount(len(self.current_items))

        for row, item in enumerate(self.current_items):
            # ID
            id_item = QTableWidgetItem(str(item['id']))
            id_item.setData(Qt.UserRole, item['id'])  # 存储ID用于详情查看
            self.result_table.setItem(row, 0, id_item)

            # 物品名称
            name_item = QTableWidgetItem(item.get('item_name', ''))
            self.result_table.setItem(row, 1, name_item)

            # 类型
            type_item = QTableWidgetItem(item.get('type', ''))
            self.result_table.setItem(row, 2, type_item)

            # 分类
            category_item = QTableWidgetItem(item.get('item_category', ''))
            self.result_table.setItem(row, 3, category_item)

            # 地点
            location_item = QTableWidgetItem(item.get('location', ''))
            self.result_table.setItem(row, 4, location_item)

            # 时间
            time_item = QTableWidgetItem(item.get('time', ''))
            self.result_table.setItem(row, 5, time_item)

            # 发布者
            publisher_item = QTableWidgetItem(item.get('publisher', ''))
            self.result_table.setItem(row, 6, publisher_item)

    def clear_search(self):
        """清空搜索条件"""
        self.search_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.category_combo.setCurrentIndex(0)
        self.perform_search()

    def show_item_detail(self, item):
        """显示物品详情"""
        row = item.row()
        item_id = self.result_table.item(row, 0).data(Qt.UserRole)

        # 查找对应的物品数据
        item_data = None
        for data in self.current_items:
            if data['id'] == item_id:
                item_data = data
                break

        if item_data:
            dialog = ItemDetailDialog(item_data, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "错误", "无法获取物品详情")

    def get_widget(self):
        """返回搜索标签页的主控件"""
        return self