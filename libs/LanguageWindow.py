# 加载本地化文件
import gettext
# 获取用户语言设置
import locale

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel, QListWidget, QListWidgetItem
from babel.messages import frontend as babel
import os
import babel.messages.pofile
from babel.messages.mofile import write_mo

LANG_DIR = 'locale'
# 获取脚本所在的绝对路径
script_path = os.path.abspath(__file__)
# 获取脚本所在的目录
script_dir = os.path.dirname(script_path)
# 获取根目录的路径（假设是上一级目录）
root_dir = os.path.dirname(script_dir)
settings = QtCore.QSettings(f"{root_dir}/ChatGptConfig.ini", QtCore.QSettings.IniFormat)
# 选择的是什么语言
LANG_CODE = 'zh_CN'

# 语言对应的选择框
langs = {
    'en_US': 'english',
    'zh_CN': '简体中文',
}
# 定义语言编码和语言文件路径
LANGUAGES = {
    'en_US': f'{LANG_DIR}/en/LC_MESSAGES/messages.po',
    'zh_CN': f'{LANG_DIR}/zh/LC_MESSAGES/messages.po',
}


# 编译语言文件
def compile_messages():
    # 遍历所有语言文件，依次编译
    for lang_code, po_file_path in LANGUAGES.items():
        mo_file_path = os.path.splitext(po_file_path)[0] + '.mo'
        with open(po_file_path, 'rb') as po_file:
            catalog = babel.messages.pofile.read_po(po_file)
            with open(mo_file_path, 'wb') as mo_file:
                write_mo(mo_file, catalog)


def init_i18n():
    """初始化翻译环境"""
    localedir = os.path.join(os.getcwd(), LANG_DIR)
    translation = gettext.translation('messages', localedir=localedir, languages=[LANG_CODE])
    translation.install()


def _(text):
    """翻译函数"""
    return gettext.translation('messages', localedir=os.path.join(os.getcwd(), LANG_DIR),
                               languages=[LANG_CODE]).gettext(text)


def init():
    global LANG_CODE
    temp = settings.value("language")
    if temp: LANG_CODE = temp


# 初始化翻译环境
init()
init_i18n()


class LanguageWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_('语言配置'))
        self.setFixedSize(500, 200)
        # 创建一个输入框和一个保存按钮
        self.list_widget = QListWidget(self)
        self.list_widget.setFixedSize(240, 160)
        self.save_button = QPushButton(_("保存"), self)
        self.save_button.setFixedSize(80, 160)

        # 添加一些项目到列表中
        for i in langs.values():
            item = QListWidgetItem(i)
            self.list_widget.addItem(item)

        # 将 itemSelectionChanged 信号连接到槽函数 on_item_selection_changed
        self.list_widget.itemSelectionChanged.connect(self.on_item_selection_changed)

        # 将输入框和保存按钮放入水平布局
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(_("语言选择："), self))
        hbox.addWidget(self.list_widget)
        hbox.addWidget(self.save_button)

        self.setLayout(hbox)

        # 为保存按钮添加点击事件处理程序
        self.save_button.clicked.connect(self.save_language)

    # 点击每一个item选择的
    def on_item_selection_changed(self):
        # 获取所选项目的文本
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            global LANG_CODE
            LANG_CODE = [item.text() for item in selected_items]
            LANG_CODE = LANG_CODE[0]
            for code, name in langs.items():
                if name == LANG_CODE:
                    LANG_CODE = code
                    break

    def save_language(self):
        gettext.bindtextdomain('myapp', '')
        gettext.textdomain('myapp')
        compile_messages()
        # 设置当前本地化环境
        locale.setlocale(locale.LC_ALL, f'{LANG_CODE}.UTF-8')
        settings.setValue("language", LANG_CODE)
        self.close()
