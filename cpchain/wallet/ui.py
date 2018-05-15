#!/usr/bin/python3
import sys, os
import os.path as osp
import string


from PyQt5.QtWidgets import (QMainWindow, QApplication, QFrame, QDesktopWidget, QPushButton, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QWidget, QScrollArea, QListWidget, QListWidgetItem, QTabWidget, QLabel,
                             QWidget, QLineEdit, QSpacerItem, QSizePolicy, QTableWidget, QFormLayout, QComboBox, QTextEdit,
                             QAbstractItemView, QTableWidgetItem, QMenu, QHeaderView, QAction, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QPoint, pyqtSignal
from PyQt5.QtGui import QIcon, QCursor, QPixmap, QStandardItem, QFont, QPainter

from cpchain import config, root_dir
# from cpchain import join_with_root

# do it before any other twisted code.
def install_reactor():
    global app
    app = QApplication(sys.argv)
    import qt5reactor; qt5reactor.install()
install_reactor()

from twisted.internet import threads, defer
from twisted.internet.task import LoopingCall

# utils
def get_icon(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QIcon(path)

def get_pixm(name):
    path = osp.join(root_dir, "cpchain/assets/wallet/icons", name)
    return QPixmap(path)

    

def load_stylesheet(wid, name):
    path = osp.join(root_dir, "cpchain/assets/wallet/qss", name)

    subs = dict(asset_dir=osp.join(root_dir, "cpchain/assets/wallet"))

    with open(path) as f:
        s = string.Template(f.read())
        wid.setStyleSheet(s.substitute(subs))


# widgets
class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        # size
        self.setMinimumWidth(self.parent.width())
        # context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        # do not highlight (bold-ize) the header
        self.horizontalHeader().setHighlightSections(False)


    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)



class HorizontalLine(QFrame):
    def __init__(self, parent=None, wid=2):
        super().__init__(parent)
        self.parent = parent
        self.wid = wid
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(self.wid)


class Product(QFrame):
    def __init__(self, parent=None, item={}):
        super().__init__(parent)
        self.parent = parent
        self.item = item
        self.init_ui()

    def init_ui(self):
        #self.frame.setMinimumWidth(500)
        self.setMinimumHeight(120)
        self.setMaximumHeight(130)
        self.title_btn = QPushButton("Medicine big data from Mayo Clinic")
        self.title_btn.setObjectName("title_btn")
        self.seller_btn = QPushButton("Barack Obama")
        self.seller_btn.setObjectName("seller_btn")
        self.seller_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.time_label = QLabel("May 4, 2018")
        self.time_label.setObjectName("time_label")
        self.total_sale_label = QLabel("128 sales")
        self.total_sale_label.setObjectName("total_sale_label")
        self.price_label = QLabel("$18")
        self.price_label.setObjectName("price_label")
        self.price_label.setFont(QFont("Arial", 15, QFont.Bold))
        self.tag = ["tag1", "tag2", "tag3", "tag4"]
        self.tag_num = 4
        self.tag_btn_list = []
        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))

        def bind_slots():
            print("Binding slots of buttons......")
        bind_slots()

        def setlayout():
            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.title_btn)
            main_layout.addSpacing(5)

            self.sales_layout = QHBoxLayout(self)
            self.sales_layout.addWidget(self.total_sale_label)
            self.sales_layout.addStretch(1)
            self.sales_layout.addWidget(self.seller_btn)
            self.sales_layout.addSpacing(5)
            self.sales_layout.addWidget(self.time_label)
            self.sales_layout.addStretch(2)
            

            self.main_layout.addLayout(self.sales_layout)
            main_layout.addSpacing(10)
            self.main_layout.addWidget(self.price_label)

            self.tag_layout = QHBoxLayout(self)
            self.tag_layout.addSpacing(1)
            for i in range(self.tag_num):
                self.tag_layout.addWidget(self.tag_btn_list[i])
                self.tag_layout.addSpacing(5)

            self.tag_layout.addStretch(1)
            self.main_layout.addLayout(self.tag_layout)
            self.setLayout(self.main_layout)
        setlayout()
        #print("Loading stylesheet of item")


class PopularTab(QScrollArea):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("popular_tab")

        self.init_ui()

    def init_ui(self):
        self.frame = QFrame()
        self.frame.setObjectName("popular_frame")
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(500)
        self.frame.setMaximumHeight(800)

        self.item_num_max = 2
        self.promo_num_max = 1

        self.horline1 = HorizontalLine(self, 2)
        self.horline1.setObjectName("horline1")
        self.horline2 = HorizontalLine(self, 2)
        self.horline2.setObjectName("horline2")

        def create_banner():
            self.banner_label = banner_label = QLabel(self)
            print("Getting banner images......")
            pixmap = get_pixm('cpc-logo-single.png')
            pixmap = pixmap.scaled(740, 195)
            banner_label.setPixmap(pixmap)
        create_banner()

        self.hot_label = QLabel("Hot Industry")
        self.hot_label.setObjectName("hot_label")
        self.hot_label.setFont(QFont("Arial", 13, QFont.Light))
        self.hot_label.setMaximumHeight(25)

        self.more_btn_1 = more_btn_1 = QPushButton("More>", self)
        more_btn_1.setObjectName("more_btn_1")
        self.more_btn_1.setCursor(QCursor(Qt.PointingHandCursor))
        #more_btn.setFixedSize(30, 18)
        self.more_btn_2 = more_btn_2 = QPushButton("More>", self)
        more_btn_2.setObjectName("more_btn_2")
        self.more_btn_2.setCursor(QCursor(Qt.PointingHandCursor))

        def create_ind_trans():
            self.trans_label = trans_label = QLabel(self)
            trans_label.setObjectName("trans_label")
            # please specify the tag of underlying picture using .setText attributes
            trans_label.setText("Transportation")
            trans_label.setFont(QFont("Arial", 13, QFont.Light))
            trans_label.setAlignment(Qt.AlignCenter)

            # please specify the file name of underlying picture using string vriable icon_name
            icon_name = 'cpc-logo-single.png'
            path = osp.join(root_dir, "cpchain/assets/wallet/icons", icon_name)

            #specify the stylesheet of this QLabel, using string variable $path
            trans_label.setStyleSheet("border-image: url({0}); color: #fefefe".format(path))
            
            print("Getting trans images......")

        create_ind_trans()

        def create_ind_forest():
            self.forest_label = forest_label = QLabel(self)
            forest_label.setObjectName("forest_label")         
            forest_label.setText("Forest")
            forest_label.setFont(QFont("Arial", 13, QFont.Light))
            forest_label.setAlignment(Qt.AlignCenter)

            # please specify the file name of underlying picture using string vriable icon_name
            icon_name = 'cpc-logo-single.png'
            path = osp.join(root_dir, "cpchain/assets/wallet/icons", icon_name)
            
            #specify the stylesheet of this QLabel, using string variable $path
            forest_label.setStyleSheet("border-image: url({0}); color: #fefefe".format(path))
            print("Getting trans images......")
        create_ind_forest()

        def create_ind_medicine():
            self.medicine_label = medicine_label = QLabel(self)
            medicine_label.setObjectName("medicine_label")
            medicine_label.setText("Medicine")
            medicine_label.setFont(QFont("Arial", 13, QFont.Light))
            medicine_label.setAlignment(Qt.AlignCenter)

            # please specify the file name of underlying picture using string vriable icon_name
            icon_name = 'cpc-logo-single.png'
            path = osp.join(root_dir, "cpchain/assets/wallet/icons", icon_name)
            
            #specify the stylesheet of this QLabel, using string variable $path
            medicine_label.setStyleSheet("border-image: url({0}); color: #fefefe".format(path))
            print("Getting trans images......")
            print("Getting trans images......")
        create_ind_medicine()

        self.recom_label = QLabel("Recommended")
        self.recom_label.setObjectName("recom_label")
        self.recom_label.setFont(QFont("Arial", 13, QFont.Light))
        self.recom_label.setMaximumHeight(25)

        def get_items():
            print("Getting items from backend......")
            self.item_lists = []
            for i in range(self.item_num_max):
                self.item_lists.append(Product(self))
        get_items()

        def get_promotion():
            print("Getting promotion images from backend.....")
            self.promo_lists = []
            for i in range(self.promo_num_max):
                promo_label = QLabel(self)
                promo_label.setObjectName("promo_label_{}".format(i))
                pixmap = get_pixm('cpc-logo-single')
                pixmap = pixmap.scaled(250, 123)
                promo_label.setPixmap(pixmap)
                self.promo_lists.append(promo_label)
        get_promotion()

        def set_layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.addWidget(self.banner_label)
            self.main_layout.addSpacing(35)
            self.main_layout.addWidget(self.hot_label)
            

            self.hot_layout = QHBoxLayout(self)
            self.hot_layout.addSpacing(0)
            self.hot_layout.addWidget(self.hot_label)
            self.hot_layout.addSpacing(50)
            self.hot_layout.addWidget(more_btn_1)
            self.main_layout.addLayout(self.hot_layout)
            self.main_layout.addSpacing(1)
            self.main_layout.addWidget(self.horline1)

            self.hot_img_layout = QHBoxLayout(self)
            self.hot_img_layout.addSpacing(25)
            self.hot_img_layout.addWidget(self.trans_label)
            self.hot_img_layout.addSpacing(25)
            self.hot_img_layout.addWidget(self.forest_label)
            self.hot_img_layout.addSpacing(25)
            self.hot_img_layout.addWidget(self.medicine_label)
            self.main_layout.addLayout(self.hot_img_layout)
            self.main_layout.addSpacing(1)
            
            self.recom_layout = QHBoxLayout(self)
            self.recom_layout.addSpacing(0)
            self.recom_layout.addWidget(self.recom_label)
            self.recom_layout.addSpacing(50)
            self.recom_layout.addWidget(more_btn_2)
            self.main_layout.addLayout(self.recom_layout)
            self.main_layout.addSpacing(1)
            self.main_layout.addWidget(self.horline2)
            self.main_layout.addSpacing(1)
            
            self.bottom_layout = QHBoxLayout(self)

            self.recom_layout = QVBoxLayout(self)
            for i in range(self.item_num_max):
                self.recom_layout.addWidget(self.item_lists[i])
                self.recom_layout.addSpacing(1)

            self.promo_layout = QVBoxLayout(self)
            for i in range(self.promo_num_max):
                self.promo_layout.addWidget(self.promo_lists[i])
                self.promo_layout.addSpacing(1)

            self.bottom_layout.addLayout(self.recom_layout)
            #self.bottom_layout.setStretchFactor(recom_layout,4)
            self.bottom_layout.addLayout(self.promo_layout)
            #self.bottom_layout.setStretch(promo_layout,1)

            self.main_layout.addLayout(self.bottom_layout)
        set_layout()
        load_stylesheet(self, "popular.qss")
        print("Loading stylesheet of cloud tab widget")



class CloudTab(QScrollArea):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("search_bar")
            self.setFixedSize(300, 25)
            self.setTextMargins(3, 0, 20, 0)

            self.search_btn_cloud = search_btn_cloud = QPushButton(self)
            search_btn_cloud.setObjectName("search_btn_cloud")
            search_btn_cloud.setFixedSize(18, 18)
            search_btn_cloud.setCursor(QCursor(Qt.PointingHandCursor))

            def bind_slots():
                print("Binding slots of clicked-search-btn......")
            bind_slots()

            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addStretch(1)
                main_layout.addWidget(search_btn_cloud)
                main_layout.setContentsMargins(0, 0, 0, 0)
                self.setLayout(main_layout)
            set_layout()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("cloud_tab")

        self.init_ui()

    def update_table(self):
        #file_list = get_file_list()
        print("Updating file list......")
        file_list = []
        # single element data structure (assumed); to be changed 
        dict_exa = {"type": "mkv", "name": "Infinity War", "size": "1.2 GB", "remote_type": "ipfs", "is_published": "published"}
        for i in range(self.row_number):
            file_list.append(dict_exa)

        for cur_row in range(self.row_number):
            if cur_row == len(file_list):
                break
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.file_table.setItem(cur_row, 0, checkbox_item)
            self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row]["type"]))
            self.file_table.setItem(cur_row, 2, QTableWidgetItem(file_list[cur_row]["name"]))
            self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row]["size"]))
            self.file_table.setItem(cur_row, 4, QTableWidgetItem(file_list[cur_row]["remote_type"]))
            self.file_table.setItem(cur_row, 5, QTableWidgetItem(file_list[cur_row]["is_published"]))

    def set_right_menu(self, func):
        self.customContextMenuRequested[QPoint].connect(func)

    def handle_upload():
            self.local_file = QFileDialog.getOpenFileName()[0]
            #defered = threads.deferToThread(upload_file_ipfs, self.local_file)
            #defered.addCallback(handle_callback_upload)

    def init_ui(self):
        self.frame = QFrame()
        self.frame.setObjectName("cloud_frame")
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(500)
        self.frame.setMaximumHeight(800)

        self.check_list = []
        self.num_file = 100
        self.total_label = total_label = QLabel("{} Files".format(self.num_file))
        total_label.setObjectName("total_label")

        self.delete_btn = delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.handle_delete)
        self.upload_btn = upload_btn = QPushButton("Upload")
        upload_btn.setObjectName("upload_btn")
<<<<<<< HEAD
        #upload_btn.clicked.connect(handle_upload)
=======
        self.upload_btn.clicked.connect(self.handle_upload)
>>>>>>> 2f4782a30f074be36588321b1286013403f511a2

        self.search_bar = CloudTab.SearchBar(self)
        self.time_label = time_label = QLabel("Time")
    
        self.row_number = 100


        def create_file_table():
            self.file_table = file_table = TableWidget(self) 

            def right_menu():
                cloud_right_menu = QMenu(file_table)
                cloud_delete_act = QAction('Delete', self)
                cloud_publish_act = QAction('Publish', self)
                cloud_open_act = QAction('Open Path...', self)

                cloud_right_menu.addAction(cloud_delete_act)
                cloud_right_menu.addAction(cloud_publish_act)
                cloud_right_menu.addAction(cloud_open_act)

                cloud_right_menu.exec_(QCursor.pos())

            file_table.horizontalHeader().setStretchLastSection(True)
            file_table.verticalHeader().setVisible(False)
            file_table.setShowGrid(False)
            file_table.setAlternatingRowColors(True)
            file_table.resizeColumnsToContents()  
            file_table.resizeRowsToContents()
            file_table.setFocusPolicy(Qt.NoFocus) 
            # do not highlight (bold-ize) the header
            file_table.horizontalHeader().setHighlightSections(False)
            file_table.setColumnCount(6)
            file_table.setRowCount(self.row_number)
            file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            file_table.set_right_menu(right_menu)
            file_table.setHorizontalHeaderLabels(['Btn_Icon', 'Type', 'Product Name', 'Size', 'Remote Type', 'Published'])
            file_table.horizontalHeader
            file_table.setSortingEnabled(True)

            #file_list = get_file_list()
            file_list = []
            print("Getting file list.......")
            dict_exa = {"type": "mkv", "name": "Infinity War", "size": "1.2 GB", "remote_type": "ipfs", "is_published": "Published"}
            for i in range(self.row_number):
                file_list.append(dict_exa)

            self.check_record_list = []
            self.checkbox_list = []
            for cur_row in range(self.row_number):
                if cur_row == len(file_list):
                    break
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox_item.setCheckState(Qt.Unchecked)
                self.file_table.setItem(cur_row, 0, checkbox_item)
                self.file_table.setItem(cur_row, 1, QTableWidgetItem(file_list[cur_row]["type"]))
                self.file_table.setItem(cur_row, 2, QTableWidgetItem(file_list[cur_row]["name"]))
                self.file_table.setItem(cur_row, 3, QTableWidgetItem(file_list[cur_row]["size"]))
                self.file_table.setItem(cur_row, 4, QTableWidgetItem(file_list[cur_row]["remote_type"]))
                self.file_table.setItem(cur_row, 5, QTableWidgetItem(file_list[cur_row]["is_published"]))
                self.check_record_list.append(False)
        create_file_table()    
        self.file_table.sortItems(2)
        # record rows that are clicked and checked
        def record_check(item):
            if item.checkState() == Qt.Checked:
                self.check_record_list[item.row()] = True
        self.file_table.itemClicked.connect(record_check)

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self)
            main_layout.addSpacing(0)
            self.layout1 = QHBoxLayout(self)
            self.layout1.addSpacing(0)
            self.layout1.addWidget(self.total_label)
            self.layout1.addStretch(1)
            self.layout1.addWidget(self.delete_btn)
            self.layout1.addSpacing(2)
            self.layout1.addWidget(self.upload_btn)
            self.layout1.addSpacing(2)

            self.main_layout.addLayout(self.layout1)
            self.main_layout.addSpacing(2)
            self.main_layout.addWidget(self.search_bar)
            self.main_layout.addSpacing(2)
            self.main_layout.addWidget(self.file_table)
            self.main_layout.addSpacing(2)
            self.setLayout(self.main_layout)
        set_layout()
        print("Loading stylesheet of cloud tab widget")
        load_stylesheet(self, "cloud.qss")

    def handle_delete(self):
        for i in range(len(self.check_record_list)):
            if self.check_record_list[i] == True:
                self.file_table.removeRow(i)
                print("Deleting files permanently from the cloud...")
                self.update_table()

    def handle_upload(self):
        # Maybe useful for buyer.
        # row_selected = self.file_table.selectionModel().selectedRows()[0].row()
        # selected_fpath = self.file_table.item(row_selected, 2).text()
        self.local_file = QFileDialog.getOpenFileName()[0]
        print("Uploading local files....")
        # defered = threads.deferToThread(upload_file_ipfs, self.local_file)
        # def handle_callback_upload(x):
        #     print("in handle_callback_upload" + x)
        #     self.update_table()
        # defered.addCallback(handle_callback_upload)
        



class SideBar(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        # needed
        self.parent = parent
        self.content_tabs = parent.content_tabs

        self.init_ui()


    def init_ui(self):
        self.setObjectName("sidebar")
        self.setMaximumWidth(180)

        self.frame = QFrame()
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(150)

        def add_labels():
            self.trend_label = QLabel("Trending")
            self.trend_label.setObjectName("trend_label")
            self.trend_label.setMaximumHeight(25)

            self.mine_label = QLabel("Mine")
            self.mine_label.setObjectName("mine_label")
            self.trend_label.setMaximumHeight(25)

            self.treasure_label = QLabel("Treasure")
            self.treasure_label.setObjectName("treasure_label")
            self.treasure_label.setMaximumHeight(25)
        add_labels()

        def add_lists():
            self.trending_list = QListWidget()
            #self.trending_list.setMinimumHeight(100)
            self.trending_list.setMaximumHeight(100)
            self.trending_list.addItem(QListWidgetItem(get_icon("pop.png"), "Popular"))
            self.trending_list.addItem(QListWidgetItem(get_icon("following.png"), "Following"))

            self.mine_list = QListWidget()
            self.mine_list.setMaximumHeight(100)
            self.mine_list.addItem(QListWidgetItem(get_icon("cloud.png"), "Cloud"))
            self.mine_list.addItem(QListWidgetItem(get_icon("store.png"), "Selling"))

            self.treasure_list = QListWidget()
            self.treasure_list.setMaximumHeight(100)
            self.treasure_list.addItem(QListWidgetItem(get_icon("purchased.png"), "Purchased"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("collection.png"), "Collection"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("collection.png"), "Shopping Cart"))

            self.trending_list.setCurrentRow(0)
        add_lists()

        def bind_slots():
            def trending_list_clicked(item):
                item_to_tab_name = {
                    "Popular": "popular_tab",
                    "Following": "follow_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.trending_list.itemPressed.connect(trending_list_clicked)

            def mine_list_clicked(item):
                item_to_tab_name = {
                    "Cloud": "cloud_tab",
                    "Selling": "selling_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.mine_list.itemPressed.connect(mine_list_clicked)

            def treasure_list_clicked(item):
                item_to_tab_name = {
                    "Purchased": "purchase_tab",
                    "Collection": "collect_tab",
                    "Shopping Cart": "cart_tab",
                }
                wid = self.content_tabs.findChild(QWidget, item_to_tab_name[item.text()])
                self.content_tabs.setCurrentWidget(wid)
            self.treasure_list.itemPressed.connect(treasure_list_clicked)

        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QVBoxLayout(self.frame)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.trend_label)
            main_layout.addSpacing(3)
            main_layout.addWidget(self.trending_list)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.mine_label)
            main_layout.addSpacing(3)
            main_layout.addWidget(self.mine_list)
            main_layout.addSpacing(1)
            main_layout.addWidget(self.treasure_label)
            main_layout.addSpacing(3)
            main_layout.addWidget(self.treasure_list)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addStretch(1)
            self.setLayout(self.main_layout)
        set_layout()
        load_stylesheet(self, "sidebar.qss")
        print("Loading stylesheet of Sidebar")


class Header(QFrame):
    class SearchBar(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.init_ui()

        def init_ui(self):
            self.setObjectName("search_bar")
            self.setFixedSize(300, 25)
            self.setTextMargins(3, 0, 20, 0)

            self.search_btn = search_btn = QPushButton(self)
            search_btn.setObjectName("search_btn")
            search_btn.setFixedSize(18, 18)
            search_btn.setCursor(QCursor(Qt.PointingHandCursor))

            def bind_slots():
                print("Binding slots of clicked-search-btn......")
            bind_slots()

            def set_layout():
                main_layout = QHBoxLayout()
                main_layout.addStretch(1)
                main_layout.addWidget(search_btn)
                main_layout.setContentsMargins(0, 0, 0, 0)
                self.setLayout(main_layout)
            set_layout()


    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()


    def init_ui(self):
        def create_logos():
            self.logo_label = logo_label = QLabel(self)
            pixmap = get_pixm('cpc-logo-single.png')
            pixmap = pixmap.scaled(45, 45)
            logo_label.setPixmap(pixmap)
            self.word_label = word_label = QLabel(self)
            self.word_label.setText("<b>CPChain</b>")
            self.word_label.setFont(QFont("Roman times", 25, QFont.Bold));
            
            print("Pic label has not been set !")
        create_logos()

        def create_search_bar():
            self.search_bar = search_bar = Header.SearchBar(self)
            search_bar.setPlaceholderText("Search")
        create_search_bar()

        def create_btns():
            self.prev_btn = QPushButton("", self)
            self.prev_btn.setObjectName("prev_btn")

            self.nex_btn = QPushButton("", self)
            self.nex_btn.setObjectName("nex_btn")

            self.download_btn = QPushButton("", self)
            self.download_btn.setObjectName("download_btn")

            self.upload_btn = QPushButton("", self)
            self.upload_btn.setObjectName("upload_btn")
            self.upload_btn.setCursor(QCursor(Qt.PointingHandCursor))

            self.message_btn = QPushButton("", self)
            self.message_btn.setObjectName("message_btn")
            self.message_btn.setCursor(QCursor(Qt.PointingHandCursor))

            self.profile_page_btn = QPushButton("", self)
            self.profile_page_btn.setObjectName("profile_page_btn")
            self.profile_page_btn.setCursor(QCursor(Qt.PointingHandCursor))

            self.profile_btn = QPushButton("", self)
            self.profile_btn.setObjectName("profile_btn")

            def create_popmenu():
                self.profile_menu = profile_menu = QMenu('Profile', self)
                profile_view_act = QAction('Profile', self)
                pro_setting_act = QAction('Profile Settins', self)
                acc_setting_act = QAction('Account Settings', self)
                bill_man_act = QAction('Bill Management', self)
                help_act = QAction('Help', self)

                profile_menu.addAction(profile_view_act)
                profile_menu.addAction(pro_setting_act)
                profile_menu.addAction(acc_setting_act)
                profile_menu.addAction(bill_man_act)
                profile_menu.addAction(help_act)
            create_popmenu()
            self.profile_btn.setMenu(self.profile_menu)

        create_btns()


        def bind_slots():
            # TODO
            print("Binding slots of clicked-search-btn......")
            print("Binding slots of pre-btn......")
            print("Binding slots of nex-btn......")
        bind_slots()

        def set_layout():
            self.main_layout = main_layout = QHBoxLayout(self)
            #main_layout.setSpacing(0)
            main_layout.addWidget(self.logo_label)
            main_layout.addSpacing(5)
            main_layout.addWidget(self.word_label)
            main_layout.addSpacing(30)
            main_layout.addWidget(self.prev_btn)
            main_layout.addWidget(self.nex_btn)
            main_layout.addSpacing(2)
            main_layout.addWidget(self.search_bar)
            main_layout.addStretch(20)
            main_layout.addWidget(self.upload_btn)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.message_btn)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.download_btn)
            main_layout.addSpacing(10)
            main_layout.addWidget(self.profile_page_btn)
            main_layout.addSpacing(5)
            main_layout.addWidget(self.profile_btn)

            self.setLayout(self.main_layout)

        set_layout()

        load_stylesheet(self, "headertest.qss")

    # drag support
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.m_DragPosition = event.globalPos() - self.parent.pos()
            self.parent.m_drag = True
            event.accept()


    def mouseMoveEvent(self, event):
        try:
            if Qt.LeftButton and event.buttons():
                self.parent.move(event.globalPos()-self.parent.m_DragPosition)
                event.accept()

        except AttributeError:
            pass


    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.m_drag = False


class MainWindow(QMainWindow):
    def __init__(self, reactor):
        super().__init__()
        self.reactor = reactor
        self.init_ui()


    def init_ui(self):
        # overall window settings
        self.setWindowTitle('CPChain Wallet')
        self.setObjectName("main_window")
        # no borders.  we make our own header panel.
        # self.setWindowFlags(Qt.FramelessWindowHint)

        def set_geometry():
            self.resize(1000, 800)  # resize before centering.
            self.setMinimumSize(800, 800)
            center_pt = QDesktopWidget().availableGeometry().center()
            qrect = self.frameGeometry()
            qrect.moveCenter(center_pt)
            self.move(qrect.topLeft())
        set_geometry()

        def add_content_tabs():
            self.content_tabs = content_tabs = QTabWidget(self)
            content_tabs.setObjectName("content_tabs")
            content_tabs.tabBar().hide()
            # Temporily modified for easy test by @hyiwr
            content_tabs.addTab(PopularTab(content_tabs), "")
            content_tabs.addTab(CloudTab(content_tabs), "")
            print("Adding tabs(browse, etc.) to content_tabs")
            print("Loading stylesheet to content_tabs")
        add_content_tabs()

        # add panes
        self.header = Header(self)
        self.sidebar = SideBar(self)


        # set layout
        def set_layout():
            self.main_layout = main_layout = QVBoxLayout()
            self.main_layout.setSpacing(0)
            self.main_layout.setContentsMargins(0, 0, 0, 0) 
            main_layout.addSpacing(0)
            main_layout.addWidget(self.header)

            self.content_layout = content_layout = QHBoxLayout()
            self.content_layout.setSpacing(0)
            self.content_layout.setContentsMargins(0, 0, 0, 0) 
            content_layout.addSpacing(0)
            content_layout.addWidget(self.sidebar)
            content_layout.addSpacing(0)
            content_layout.addWidget(self.content_tabs)

            self.main_layout.addLayout(self.content_layout)

            wid = QWidget(self)
            wid.setLayout(self.main_layout)
            self.setCentralWidget(wid)
        set_layout()
        load_stylesheet(self, "main_window.qss") 
        print("Seting stylesheet of MainWindow......")
          
        self.show()


    def closeEvent(self, event):
        self.reactor.stop()



def _handle_keyboard_interrupt():
    def sigint_handler(*args):
        QApplication.quit()

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    # cf. https://stackoverflow.com/a/4939113/855160
    from PyQt5.QtCore import QTimer

    # make it global, o.w. the timer will soon vanish.
    _handle_keyboard_interrupt.timer = QTimer()
    timer = _handle_keyboard_interrupt.timer
    timer.start(300) # run each 300ms
    timer.timeout.connect(lambda: None)


    
def initialize_system():
    def initialize_net():
        # Temporily modified for easy test by @hyiwr
        print("Initializing network......")
    initialize_net()
    
    def monitor_chain_event():
        # Temporily modified for easy test by @hyiwr
        print("Monitoring chain event......")
    monitor_chain_event()


def main():
    global main_wnd
    from twisted.internet import reactor
    main_wnd = MainWindow(reactor)
    _handle_keyboard_interrupt()

    initialize_system()
    
    sys.exit(reactor.run())


if __name__ == '__main__':
    main()
