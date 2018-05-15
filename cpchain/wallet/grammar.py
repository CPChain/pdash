class Item(QFrame):
    def __init__(self, parent=None, item={}):
        super().__init__(parent)
        self.parent = parent
        self.item = item

        self.init_ui()
    def init_ui(self):
        self.name_btn = QPushButton("Medicine big data from Mayo Clinic")
        self.seller_btn = QPushButton("Barack Obama")
        self.time_label = QLabel("May 4, 2018")
        self.price_label = QLabel()


class ItemArea(QScrollArea):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.init_ui()

    def init_ui(self):
        self.setObjectName("itemarea")
        self.setMaximumWidth(180)

        self.frame = QFrame()
        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(150)

        def add_lists():
            self.trending_list = QListWidget()
            self.trending_list.addItem(QListWidgetItem(get_icon("cloud_store.png"), "Popular"))
            self.trending_list.addItem(QListWidgetItem(get_icon("publish_data.png"), "Following"))

            self.mine_list = QListWidget()
            self.mine_list.addItem(QListWidgetItem(get_icon("browse_market.png"), "Cloud"))
            self.mine_list.addItem(QListWidgetItem(get_icon("treasur.png"), "Selling"))

            self.treasure_list = QListWidget()
            self.treasure_list.addItem(QListWidgetItem(get_icon("browse_market.png"), "Purchased"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("browse_market.png"), "Collection"))
            self.treasure_list.addItem(QListWidgetItem(get_icon("browse_market.png"), "Shopping Cart"))

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
            main_layout.addSpacing(0)
            main_layout.addWidget(self.trend_label)
            main_layout.addWidget(self.trending_list)
            main_layout.addWidget(self.mine_label)
            main_layout.addWidget(self.mine_list)
            main_layout.addWidget(self.treasure_label)
            main_layout.addWidget(self.treasure_list)
            main_layout.setContentsMargins(0, 10, 0, 0)
            self.setLayout(self.main_layout)
        set_layout()

        print("Loading stylesheet of Sidebar")