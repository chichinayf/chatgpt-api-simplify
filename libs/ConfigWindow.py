import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPlainTextEdit, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit

# 创建配置窗口
from libs import MyMainWindow
from libs.LanguageWindow import _, init_i18n

# 初始化翻译环境
init_i18n()


class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, settings):
        super().__init__()

        self.setWindowTitle(_('参数配置'))
        self.setFixedSize(600, 500)
        self.settings = settings
        self.get_settings()
        # 创建一个输入框和一个保存按钮
        self.input_box1 = QLineEdit(self)
        self.input_box2 = QLineEdit(self)
        self.input_box3 = QLineEdit(self)
        self.input_box4 = QPlainTextEdit(self)
        self.input_box5 = QLineEdit(self)
        self.save_button = QPushButton(_("保存"), self)
        self.input_box1.setFixedSize(400, 80)
        self.input_box2.setFixedSize(400, 80)
        self.input_box3.setFixedSize(400, 80)
        self.input_box4.setFixedSize(400, 80)
        self.input_box5.setFixedSize(400, 80)
        self.save_button.setFixedHeight(100)
        # 设置默认值
        self.input_box1.setText(self.settings.value("proxy", ""))
        self.input_box2.setText(self.settings.value("url", ""))
        self.input_box3.setText(self.settings.value("key", ""))
        self.input_box4.setPlainText(self.settings.value("params", ""))
        self.input_box5.setText(self.settings.value("length", ""))

        # 将输入框和保存按钮放入水平布局
        hbox1 = QHBoxLayout()
        hbox1.addWidget(QLabel(_("代理："), self))
        hbox1.addWidget(self.input_box1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel(_("接口URL："), self))
        hbox2.addWidget(self.input_box2)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(QLabel(_("接口秘钥："), self))
        hbox3.addWidget(self.input_box3)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(QLabel(_("JSON参数："), self))
        hbox4.addWidget(self.input_box4)

        hbox5 = QHBoxLayout()
        hbox5.addWidget(QLabel(_("回溯长度："), self))
        hbox5.addWidget(self.input_box5)

        # 竖直
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addWidget(self.save_button)
        self.setLayout(vbox)

        # 为保存按钮添加点击事件处理程序
        self.save_button.clicked.connect(self.save_settings)

    def save_settings(self):
        input_box1 = self.input_box1.text()
        input_box2 = self.input_box2.text()
        input_box3 = self.input_box3.text()
        input_box4 = self.input_box4.toPlainText()
        input_box5 = self.input_box5.text()
        self.settings.setValue("proxy", input_box1)
        self.settings.setValue("url", input_box2)
        self.settings.setValue("key", input_box3)
        self.settings.setValue("params", input_box4)
        self.settings.setValue("length", input_box5)
        self.get_settings()
        # 关闭窗口
        self.close()

    # 读取配置到全局参数中
    def get_settings(self):
        url_ = QtWidgets.QLabel(self.settings.value("url", "")).text()
        if url_:
            MyMainWindow.url = url_
        else:
            QtWidgets.QLabel(self.settings.setValue("url", MyMainWindow.url))
        key_ = QtWidgets.QLabel(self.settings.value("key", "")).text()
        if key_:
            MyMainWindow.key = key_
        else:
            QtWidgets.QLabel(self.settings.setValue("key", MyMainWindow.url))
        proxy_ = QtWidgets.QLabel(self.settings.value("proxy", "")).text()
        if proxy_:
            MyMainWindow.proxy = proxy_
        else:
            QtWidgets.QLabel(self.settings.setValue("proxy", MyMainWindow.proxy))
        params_ = QtWidgets.QLabel(self.settings.value("params", "")).text()
        if params_:
            params = params_
            MyMainWindow.params = json.loads(params.replace(",\n}", "\n}"))
        else:
            QtWidgets.QLabel(self.settings.setValue("params", params_))
        length_ = QtWidgets.QLabel(self.settings.value("length", "")).text()
        if length_:
            MyMainWindow.length = length_
        else:
            QtWidgets.QLabel(self.settings.setValue("length", MyMainWindow.length))