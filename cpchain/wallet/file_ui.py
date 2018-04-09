import tempfile, os
from cpchain.utils import sizeof_fmt

from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QTableWidget, \
    QAbstractItemView, QTableWidgetItem, QPushButton, QFileDialog
from cpchain.wallet.fs import *


class FileTab(QScrollArea):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.row_number = 20
        self.init_ui()

    def init_ui(self):

        def create_file_table():
            self.file_table = file_table = QTableWidget()

            file_table.setMinimumWidth(self.width())
            file_table.setColumnCount(4)
            file_table.setRowCount(self.row_number)
            file_table.setHorizontalHeaderLabels(['File Name', 'File Size', 'Remote Type', 'Published'])

            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)

            file_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)

            file_list = get_file_list()
            for cur_row in range(self.row_number):
                if cur_row == file_list.__len__():
                    break
                file_table.setItem(cur_row, 0, QTableWidgetItem(file_list[cur_row].name))
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(file_list[cur_row].remote_type))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(str(file_list[cur_row].is_published)))

        create_file_table()

        def update_table():
            file_list = get_file_list()
            for cur_row in range(self.row_number):
                if cur_row == file_list.__len__():
                    break
                self.file_table.setItem(cur_row, 0, QTableWidgetItem(file_list[cur_row].name))
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(sizeof_fmt(file_list[cur_row].size)))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(file_list[cur_row].remote_type))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(str(file_list[cur_row].is_published)))


        def handle_upload_button():
            # Maybe useful for buyer.
            # row_selected = self.file_table.selectionModel().selectedRows()[0].row()
            # selected_fpath = self.file_table.item(row_selected, 2).text()
            local_file = QFileDialog.getOpenFileName()[0]
            with tempfile.TemporaryDirectory() as tmpdirname:
                encrypted_path = os.path.join(tmpdirname, 'encrypted.txt')
                encrypt_file(local_file, encrypted_path)
                hash_code = upload_file_ipfs(encrypted_path)
                file_name = list(os.path.split(local_file))[-1]
                file_size = os.path.getsize(local_file)
                new_file_info = FileInfo(hashcode=hash_code, name=file_name, path=local_file, size=file_size,
                                         remote_type="ipfs", remote_uri="/ipfs/" + file_name, is_published=False)
                add_file(new_file_info)
                update_table()

        def create_buttons():
            self.upload_button = upload_button = QPushButton('Encrypt and Upload')
            upload_button.clicked.connect(handle_upload_button)

        create_buttons()

        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.file_table)
            self.main_layout.addWidget(self.upload_button)

        set_layout()





