from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QScrollArea, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QGridLayout, QPushButton,
                             QMenu, QAction, QCheckBox, QVBoxLayout)
from PyQt5.QtGui import QCursor

from cpchain.wallet.pages import load_stylesheet, HorizontalLine

class Seller(QScrollArea):
    def __init__(self, parent=None, sellerid=None, mode=""):
        super().__init__(parent)
        self.parent = parent
        self.sellerid = sellerid
        self.mode = mode
        self.init_ui()

    def init_ui(self):
        self.setMinimumHeight(200)
        self.setMaximumHeight(500)
        self.setMinimumHeight(120)
        self.setMaximumHeight(120)
        self.seller_name = QPushButton("Barack Obama")
        self.seller_name.setObjectName("seller_name")
        self.seller_name.setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_avatar = QLabel(self)
        self.seller_avatar.setObjectName("seller_avatar")

        seller_product_value = 20
        seller_sales_volume = 3455
        self.product_label = QLabel("Products {}".format(seller_product_value))
        self.sales_volume = QLabel("Sales Volume {}".format(seller_sales_volume))

        self.hline = HorizontalLine(self, 2)

        self.main_layout = QGridLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.seller_avatar, 1, 1, 2, 3)
        self.main_layout.addWidget(self.seller_name, 1, 3, 1, 1)
        self.main_layout.addWidget(self.product_label, 2, 3, 1, 1)
        self.main_layout.addWidget(self.sales_volume, 3, 3, 1, 1)
        self.main_layout.addWidget(self.hline, 4, 1, 1, 3)
        self.setLayout(self.main_layout)
        load_stylesheet(self, "selleritem.qss")

class PersonalProfileTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("personalprofile_tab")
        self.init_ui()

    def init_ui(self):

        self.profile_tabs = profile_tabs = QTabWidget(self)
        profile_tabs.setObjectName("profile_tabs")
        profile_tabs.addTab(PersonalInfoPage(profile_tabs), "Personal Information")
        profile_tabs.addTab(PreferenceTab(profile_tabs), "Preference")
        profile_tabs.addTab(SecurityTab(profile_tabs), "Account Security")

        def set_layout():
            follow_main_layout = QHBoxLayout()
            follow_main_layout.addWidget(self.profile_tabs)
            self.setLayout(follow_main_layout)
        set_layout()
        load_stylesheet(self, "personalprofile.qss")

    def set_one_index(self):
        self.profile_tabs.setCurrentIndex(0)

    def set_two_index(self):
        self.profile_tabs.setCurrentIndex(1)

    def set_three_index(self):
        self.profile_tabs.setCurrentIndex(2)

class SecurityTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("securitypage")
        self.init_ui()

    def init_ui(self):
        self.balance_label = balance_label = QLabel("Account Balance:")
        balance_label.setObjectName("balance_label")
        self.password_label = password_label = QLabel("Payment Password:")
        password_label.setObjectName("password_label")
        self.accountbinding_label = accountbinding_label = QLabel("Account Binding:")
        accountbinding_label.setObjectName("accountbinding_label")
        self.paylimit_label = paylimit_label = QLabel("Daily Payment Limit:")
        paylimit_label.setObjectName("paylimit_label")

        balance = 9999
        self.balance_value = balance_value = QLabel("{} CPC".format(balance))
        balance_label.setObjectName("balance_label")

        bindingaccout = str("Barack Obama")
        self.binding_label = binding_label = QLabel("{} Account".format(bindingaccout))
        binding_label.setObjectName("binding_label")

        self.cpc_label = cpc_label = QLabel("CPC")
        cpc_label.setObjectName("cpc_label")

        self.password_edit = password_edit = QLineEdit()
        password_edit.setObjectName("password_edit")
        password_edit.setEchoMode(QLineEdit.Password)

        self.paylimit_edit = paylimit_edit = QLineEdit()
        paylimit_edit.setObjectName("paylimit_edit")

        self.display_btn = display_btn = QPushButton("Display Balance")
        self.display_btn.setObjectName("display_btn")
        self.display_btn.clicked.connect(self.handle_display)
        self.reset_btn = reset_btn = QPushButton("Reset Password")
        self.reset_btn.setObjectName("reset_btn")

        self.reset_btn.clicked.connect(self.handle_reset)

        self.security_layout = security_layout = QGridLayout(self)
        self.security_layout.setContentsMargins(40, 40, 150, 300)
        self.security_layout.addWidget(balance_label, 1, 1, 1, 1)

        self.balance_layout = balance_layout = QVBoxLayout(self)
        self.balance_layout.addStretch(1)
        self.balance_layout.addWidget(balance_value)
        self.balance_layout.addSpacing(10)
        self.balance_layout.addWidget(display_btn)
        self.balance_layout.addStretch(2)

        self.security_layout.addLayout(balance_layout, 1, 3, 2, 4)

        self.security_layout.addWidget(password_label, 3, 1, 1, 1)
        self.security_layout.addWidget(password_edit, 3, 3, 1, 5)
        self.security_layout.addWidget(reset_btn, 4, 3, 1, 2)

        self.security_layout.addWidget(accountbinding_label, 5, 1, 1, 1)
        self.security_layout.addWidget(binding_label, 5, 3, 1, 2)
        self.security_layout.addWidget(paylimit_label, 6, 1, 1, 1)
        self.security_layout.addWidget(paylimit_edit, 6, 3, 1, 2)
        self.security_layout.addWidget(cpc_label, 6, 5, 1, 2)

        self.setLayout(security_layout)
        load_stylesheet(self, "security.qss")

    def handle_display(self):
        pass

    def handle_reset(self):
        pass

class PersonalInfoPage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("PersonalInfoPage")
        self.init_ui()

    def init_ui(self):
        self.avatar_label = avatar_label = QLabel("Avatar")
        avatar_label.setObjectName("avatar_label")
        self.avatar_icon = avatar_icon = QLabel("ICONHERE")
        avatar_icon.setObjectName("avatar_icon")
        self.username_label = username_label = QLabel("Username:")
        username_label.setObjectName("username_label")
        self.email_label = email_label = QLabel("Email:")
        email_label.setObjectName("email_label")
        self.gender_label = gender_label = QLabel("Gender:")
        gender_label.setObjectName("gender_label")
        self.phone_label = phone_label = QLabel("Mobile Phone")
        phone_label.setObjectName("phone_label")

        self.username_edit = username_edit = QLineEdit()
        username_edit.setObjectName("username_edit")
        self.email_edit = email_edit = QLineEdit()
        email_edit.setObjectName("email_edit")
        self.phone_edit = phone_edit = QLineEdit()
        phone_edit.setObjectName("phone_edit")


        self.avataripload_btn = avataripload_btn = QPushButton(self)
        self.avataripload_btn.setObjectName("avataripload_btn")
        self.avataripload_btn.setText("Upload/Save")
        self.avataripload_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.avataripload_btn.clicked.connect(self.handle_submit)

        self.gender_btn = gender_btn = QPushButton(self)
        self.gender_btn.setObjectName("gender_btn")

        self.submit_btn = submit_btn = QPushButton(self)
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.setText("Submit")
        self.submit_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.submit_btn.clicked.connect(self.handle_submit)

        self.gender_menu = gender_menu = QMenu('Gender', self)
        self.male_act = QAction('Male', self)
        self.male_act.triggered.connect(self.set_male_act)
        self.female_act = QAction('Female', self)
        self.female_act.triggered.connect(self.set_female_act)
        self.others_act = QAction('Other', self)
        self.others_act.triggered.connect(self.set_other_act)
        gender_menu.addAction(self.male_act)
        gender_menu.addAction(self.female_act)
        gender_menu.addAction(self.others_act)
        self.gender_btn.setMenu(self.gender_menu)
        self.pinfo_top_layout = pinfo_top_layout = QGridLayout(self)
        self.pinfo_top_layout.setContentsMargins(40, 40, 300, 100)
        self.pinfo_top_layout.addWidget(avatar_label, 1, 1, 1, 1)
        self.pinfo_top_layout.addWidget(avatar_icon, 1, 3, 3, 3)
        self.pinfo_top_layout.addWidget(avataripload_btn, 4, 3, 1, 1)
        self.pinfo_top_layout.addWidget(username_label, 5, 1, 1, 1)
        self.pinfo_top_layout.addWidget(username_edit, 5, 3, 1, 5)
        self.pinfo_top_layout.addWidget(email_label, 6, 1, 1, 1)
        self.pinfo_top_layout.addWidget(email_edit, 6, 3, 1, 20)
        self.pinfo_top_layout.addWidget(gender_label, 7, 1, 1, 1)
        self.pinfo_top_layout.addWidget(gender_btn, 7, 3, 1, 1)
        self.pinfo_top_layout.addWidget(phone_label, 8, 1, 1, 1)
        self.pinfo_top_layout.addWidget(phone_edit, 8, 3, 1, 20)
        self.pinfo_top_layout.addWidget(submit_btn, 10, 3, 1, 2)
        self.setLayout(pinfo_top_layout)
        load_stylesheet(self, "personalinfotab.qss")
    def set_male_act(self):
        self.gender_btn.setText("Male")
    def set_female_act(self):
        self.gender_btn.setText("Female")
    def set_other_act(self):
        self.gender_btn.setText("Other")
    def handle_submit(self):
        pass


class PreferenceTab(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("preferencepage")
        self.init_ui()

    def init_ui(self):
        self.downloadpath_label = downloadpath_label = QLabel("Download Path:")
        downloadpath_label.setObjectName("downloadpath_label")
        self.tips_label = tips_label = QLabel("Send message in these conditions:")
        tips_label.setObjectName("tips_label")
        self.messageset_label = messageset_label = QLabel("Message Setting:")
        messageset_label.setObjectName("messageset_label")
        self.tag_label = tag_label = QLabel("Following Tags:")
        tag_label.setObjectName("tag_label")
        self.seller_label = seller_label = QLabel("Following Sellers:")
        seller_label.setObjectName("seller_label")

        self.downloadpath_edit = downloadpath_edit = QLineEdit()
        downloadpath_edit.setObjectName("downloadpath_edit")

        self.tag = ["tag1", "tag2", "tag3", "tag4"]
        self.tag_num = 4
        self.tag_btn_list = []
        for i in range(self.tag_num):
            self.tag_btn_list.append(QPushButton(self.tag[i], self))
            self.tag_btn_list[i].setObjectName("tag_btn_{0}".format(i))
            self.tag_btn_list[i].setProperty("t_value", 1)
            self.tag_btn_list[i].setCursor(QCursor(Qt.PointingHandCursor))

        self.seller_list = []
        self.seller_follow_number = 2

        def get_seller_list():
            for i in range(self.seller_follow_number):
                self.seller_list.append(Seller(self))

        get_seller_list()

        self.sellerid = {"name": "Chak", "sales": "2020"}
        self.openpath_btn = openpath_btn = QPushButton(self)
        self.openpath_btn.setObjectName("openpath_btn")
        self.openpath_btn.setText("Open...")
        self.openpath_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.openpath_btn.clicked.connect(self.handle_openpath)

        self.addtag_btn = addtag_btn = QPushButton(self)
        self.addtag_btn.setObjectName("addtag_btn")
        self.addtag_btn.setText("Add...")
        self.addtag_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.addtag_btn.clicked.connect(self.handle_addtag)

        self.messageset_checkbox_1 = messageset_checkbox_1 = QCheckBox(self)
        self.messageset_checkbox_1.setObjectName("messageset_checkbox_1")
        self.messageset_checkbox_1.setText("New Order")

        self.messageset_checkbox_2 = messageset_checkbox_2 = QCheckBox(self)
        self.messageset_checkbox_2.setObjectName("messageset_checkbox_2")
        self.messageset_checkbox_2.setText("Account spending")

        self.messageset_checkbox_3 = messageset_checkbox_3 = QCheckBox(self)
        self.messageset_checkbox_3.setObjectName("messageset_checkbox_3")
        self.messageset_checkbox_3.setText("Download failed")

        product_counter = 20
        self.seller_avatar = seller_avatar = QLabel("ICONHERE")
        seller_avatar.setObjectName("seller_avatar")
        self.seller_id = seller_id = QLabel("Christopher Chak")
        seller_id.setObjectName("seller_id")
        self.seller_pcount = seller_pcount = QLabel("Products {}".format(product_counter))
        seller_pcount.setObjectName("seller_pcount")
        self.unfollow_btn = QPushButton("Unfollow")
        self.unfollow_btn.setObjectName("unfollow_btn")
        self.unfollow_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.unfollow_btn.clicked.connect(self.handle_unfollow)


        self.pinfo_preference_layout = pinfo_preference_layout = QGridLayout(self)
        #self.pinfo_top_layout.setSpacing(10)
        self.pinfo_preference_layout.setContentsMargins(40, 40, 150, 100)
        self.pinfo_preference_layout.addWidget(downloadpath_label, 1, 1, 1, 1)
        self.pinfo_preference_layout.addWidget(downloadpath_edit, 1, 3, 1, 10)
        self.pinfo_preference_layout.addWidget(openpath_btn, 2, 3, 1, 2)

        self.pinfo_preference_layout.addWidget(messageset_label, 3, 1, 1, 1)
        self.pinfo_preference_layout.addWidget(tips_label, 3, 3, 1, 5)
        self.pinfo_preference_layout.addWidget(messageset_checkbox_1, 4, 3, 1, 2)
        self.pinfo_preference_layout.addWidget(messageset_checkbox_2, 5, 3, 1, 2)
        self.pinfo_preference_layout.addWidget(messageset_checkbox_3, 6, 3, 1, 2)

        self.pinfo_preference_layout.addWidget(tag_label, 7, 1, 1, 1)
        self.pinfo_tag_layout = pinfo_tag_layout = QHBoxLayout(self)
        for i in range(self.tag_num):
            self.pinfo_tag_layout.addWidget(self.tag_btn_list[i])
            self.pinfo_tag_layout.addSpacing(5)

        self.pinfo_tag_layout.addStretch(1)
        self.pinfo_preference_layout.addLayout(pinfo_tag_layout, 7, 3, 1, 10)
        self.pinfo_preference_layout.addWidget(addtag_btn, 8, 3, 1, 2)

        self.pinfo_preference_layout.addWidget(seller_label, 9, 1, 1, 1)

        self.seller_layout = seller_layout = QVBoxLayout(self)

        for i in range(self.seller_follow_number):
            self.seller_layout.addWidget(self.seller_list[i])
            self.seller_layout.addSpacing(0)

        self.pinfo_preference_layout.addLayout(seller_layout, 9, 3, 5, 6)
        self.setLayout(pinfo_preference_layout)
        load_stylesheet(self, "preference.qss")

    def handle_openpath(self):
        pass

    def handle_addtag(self):
        pass

    def handle_unfollow(self):
        pass

