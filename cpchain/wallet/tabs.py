from PyQt5.QtWidgets import (QScrollArea, QFormLayout, QVBoxLayout, QComboBox, QLineEdit, QLabel,
                             QTextEdit, QTableWidget, QPushButton)


class BrowseTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("browse_tab")
        self.init_ui()

    def init_ui(self):

        def create_item_table():
            self.item_table = item_table = QTableWidget(self)
            item_table.setObjectName("item_table")

            headers = ["Title", "Size", "Price"]
            item_table.setColumnCount(len(headers))
            item_table.setHorizontalHeaderLabels(headers)
            item_table.setMinimumWidth(self.width())

            item_table.setAlternatingRowColors(True)

            item_table.horizontalHeader().setStretchLastSection(True)

            # item_table.setColumnWidth(0, self.width()/3*1.25)

            # item_table.verticalHeader().setVisible(False)
            # item_table.setShowGrid(False)
            # item_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            # item_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        create_item_table()


        def set_layout():
            main_layout = QVBoxLayout(self)
            main_layout.addWidget(self.item_table)

        set_layout()


            
class PublishTab(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setObjectName("publish_tab")

        self.init_ui()

    def init_ui(self):

        def set_layout():
            main_layout = QFormLayout(self)
            self.data_item = QComboBox()
            self.data_title = QLineEdit()
            self.data_desc = QTextEdit()
            self.data_tags = QLineEdit()

            main_layout.addRow(QLabel("Data"), self.data_item)
            main_layout.addRow(QLabel("Title"), self.data_title)
            main_layout.addRow(QLabel("Description"), self.data_desc)
            main_layout.addRow(QLabel("Tag"), self.data_tags)


            publish_btn = QPushButton('Publish')
            publish_btn.clicked.connect(self.publish_data)

            main_layout.addWidget(publish_btn)

        set_layout()


    def publish_data(self):
        print(self.data_title.text())
