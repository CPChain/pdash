from PyQt5.QtWidgets import QScrollArea, QFormLayout, QComboBox, QLineEdit, QLabel, QTextEdit, QPushButton


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
