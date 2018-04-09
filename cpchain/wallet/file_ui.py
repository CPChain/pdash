from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QTableWidget, QAbstractItemView


class FileTab(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):

        def create_file_table():
            self.file_table = file_table = QTableWidget()

            file_table.setMinimumWidth(self.width())
            file_table.setColumnCount(3)
            file_table.setHorizontalHeaderLabels(['File Name', 'File Size', 'Etc.'])

            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)

            file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        create_file_table()


        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.file_table)

        set_layout()


