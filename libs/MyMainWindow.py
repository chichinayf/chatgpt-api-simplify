import html as htmls
import json
import os
import threading
from datetime import datetime
from time import sleep

import requests
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget, QListWidget, \
    QDesktopWidget, QPushButton, QHBoxLayout, QAction, QMessageBox, QMenu, QShortcut, QInputDialog, QLineEdit
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.styles import get_all_styles

# 定义模板字符串
from libs.ConfigWindow import ConfigWindow
from libs.LanguageWindow import LanguageWindow, init_i18n, _
from libs.SqlUtils import execute_query_sql, execute_update_sql, save_data_to_database

# 初始化翻译环境
init_i18n()
# 所有的需要修改的参数
proxy = "127.0.0.1:19180"
url = "https://api.openai.com/v1/chat/completions"
key = ""
params = {
    "model": "gpt-3.5-turbo",
    "messages": [],
    # "temperature": 0.7,
    # "max_tokens": 4096,
    # "n": 1,
}
length = "5"
now = datetime.now()
# 将时间格式化为指定格式的字符串
formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')

my_css = """
    .language-Basic,
    .language-Pascal,
    .language-Object Pascal,
    .language-C,
    .language-C++,
    .language-C#,
    .language-Java,
    .language-ASP,
    .language-ASP.NET,
    .language-Perl,
    .language-PHP,
    .language-SQL,
    .language-FoRTRAN,
    .language-Visual Basic,
    .language-Visual Basic.NET,
    .language-Delphi,
    .language-Visual C++,
    .language-C++ Builder,
    .language-C# Builder,
    .language-Python,
    .language-python,
    .language-Go,
    .language-go,
    .language-Visual Foxpro,
    .language-css,
    .language-html{
        border:1px solid #dddddd;
        border-radius:10px;
    }
    code {
        border: 1px solid #dddddd;
        border-radius: 10px;
        padding: 2px;
        clear: both;
        display: flex;
        padding: 10px;
        background-color: black;
        margin: 0px 10px;
    }
    div{
        color:white; 
    }
    .highlight {
        background: black;
        padding: 4px 10px;
    }
    .s1,.s2{
        background-color: black !important;
        color: darkturquoise !important;
    }
    ::-webkit-scrollbar {
      width: 6px; /* 竖向滚动条宽度 */
      height: 6px; /* 横向滚动条高度 */
    }

    ::-webkit-scrollbar-thumb {
      border-radius: 10px; /* 滚动条样式 */
      background-color: black; /* 滚动条颜色 */
    }

    ::-webkit-scrollbar-thumb:hover {
      background-color: black; /* 滚动条悬浮颜色 */
    }

    ::-webkit-scrollbar-track-piece {
      background: black; /* 滚动条背景颜色 */
    }

    ::-webkit-scrollbar-button {
    }

    ::-webkit-scrollbar-corner {
    }


    /* 单独设置悬浮颜色 */
    ::-webkit-scrollbar-thumb:vertical {
      background: darkgray;  /* 竖向滑块颜色 */
    }
    ::-webkit-scrollbar-thumb:horizontal {
      background: darkgray; /* 横向滑块颜色 */
    }

    /* 单独设置滚动条背景色 */
    ::-webkit-scrollbar-track-piece:vertical {
      background: white;
    }
    ::-webkit-scrollbar-track-piece:horizontal {
      background: white;
    }

"""
html_top1 = '''
<html>
  <head>
    <style>
'''

html_top2 = '''
    </style>
  </head>
  <body style="padding:4px;">
'''

html_bottom = '''
  </body>
</html>
'''

selectRowStr = ""
all_res_root = {}
all_res = {}
all_res_index = {}


# 主窗口
class MyMainWindow(QtWidgets.QMainWindow):
    data_ready = QtCore.pyqtSignal(str, )
    data_error = QtCore.pyqtSignal(str, )
    data_loading = QtCore.pyqtSignal(bool, )

    def __init__(self):
        super().__init__()
        self.data_ready.connect(self.update_ui)
        self.data_error.connect(self.error_ui)
        self.data_loading.connect(self.loading_ui)
        self.setWindowTitle("ChatGpt")
        self.setGeometry(0, 0, 1400, 800)
        self.center()

        # 创建菜单栏和一个“配置”菜单
        menubar = self.menuBar()
        config_menu = menubar.addMenu(_("配置"))

        # 创建一个“配置”动作并将其添加到“配置”菜单
        config_action = QAction(_("配置"), self)
        config_action.triggered.connect(self.show_config_dialog)
        config_menu.addAction(config_action)
        # 创建一个“语言”动作并将其添加到“配置”菜单

        language_action = QAction(_("语言"), self)
        language_action.triggered.connect(self.show_language_dialog)
        config_menu.addAction(language_action)
        # 创建一个配置窗口
        # 获取脚本所在的绝对路径
        script_path = os.path.abspath(__file__)
        # 获取脚本所在的目录
        script_dir = os.path.dirname(script_path)
        # 获取根目录的路径（假设是上一级目录）
        root_dir = os.path.dirname(script_dir)
        self.settings = QtCore.QSettings(f"{root_dir}/ChatGptConfig.ini", QtCore.QSettings.IniFormat)
        self.config_window = ConfigWindow(self.settings)
        # 创建一个语言切换窗口
        self.language_window = LanguageWindow()

        # 创建一个标签，显示从数据库中获取的数据
        # self.data_label = QLabel(_("从数据库中获取的数据："), self)
        # self.data_label.move(10, 50)
        # self.data_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 在左边新增一个列表选择框
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(200)
        fields, self.rows = execute_query_sql("select * from chats where is_del = 0 or is_del = null  group by types",
                                              ())
        rows_str = []
        for row in self.rows:
            rows_str.append(row[1])
        self.list_widget.addItems(rows_str)
        self.list_widget.currentItemChanged.connect(self.on_list_item_changed)
        # 为QListWidget的右键单击事件绑定槽函数
        self.list_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        # 下面新增一个增加对话框的按钮
        self.text_add_button = QPushButton()
        self.text_add_button.setText(_("新增对话"))
        self.text_add_button.setFixedWidth(200)
        self.text_add_button.clicked.connect(self.send_text_add_button)

        # 新增一个webview
        # self.text_edit_input1 = QPlainTextEdit()
        # self.text_edit_input1.setFixedWidth(500)
        # self.text_edit_input1.setFixedHeight(700)
        self.web_view = QWebEngineView()
        # self.text_edit_input1.setFixedHeight(700)
        self.web_view.loadFinished.connect(self.on_load_finished)
        # ctrl + f按下后就会调用 show_search_dialog 方法
        self.shortcut = QShortcut(Qt.CTRL + Qt.Key_F, self.web_view)
        self.shortcut.activated.connect(self.show_search_dialog)

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search)

        # 新增一个用户发送框
        self.text_edit_input = QPlainTextEdit(self)
        self.text_edit_input.setFixedHeight(100)
        self.text_edit_input.installEventFilter(self)
        # 用户输入的问题发送按钮
        self.text_edit_button = QPushButton()
        self.text_edit_button.setText(_("发送"))
        self.text_edit_button.setFixedWidth(200)
        self.text_edit_button.setFixedHeight(100)
        self.text_edit_button.clicked.connect(self.send_message)

        # 窗口所有的布局
        # 竖直放置
        vBox = QVBoxLayout()
        vBox2 = QVBoxLayout()
        vBox.addWidget(self.list_widget)
        vBox.addWidget(self.text_add_button)
        hBox0 = QHBoxLayout()
        hBox0.addWidget(self.web_view)
        # hBox0.addWidget(self.text_edit_input1)
        hBox1 = QHBoxLayout()
        hBox1.addWidget(self.text_edit_input)
        hBox1.addWidget(self.text_edit_button)
        vBox2.addLayout(hBox0)
        vBox2.addLayout(hBox1)
        # 水平放置
        hBox = QHBoxLayout()
        hBox.addLayout(vBox)
        hBox.addLayout(vBox2)

        central_widget = QWidget()
        central_widget.setLayout(hBox)
        self.setCentralWidget(central_widget)

        # 初始化Pygments样式表
        self.formatter = HtmlFormatter(style='colorful', full=True)
        self.css = self.formatter.get_style_defs('.highlight')

        # 显示初始预览
        self.update_preview()

    def search(self):
        text = self.search_bar.text()
        self.web_view.findText(text, QWebEnginePage.FindCaseSensitively)

    def show_search_dialog(self):
        # 搜索框
        text, ok = QInputDialog.getText(self, _("搜索"), _("输入搜索的内容:"))
        if ok and text:
            self.search_bar.setText(text)
            self.search()

    def closeEvent(self, event):
        self.config_window.close()
        self.language_window.close()
        event.accept()

    def show_context_menu(self, pos):
        # 创建QMenu并添加选项
        menu = QMenu(self.list_widget)
        delete_action = menu.addAction(_("删除"))
        refresh_action = menu.addAction(_("刷新"))  # 显示菜单
        action = menu.exec_(self.list_widget.mapToGlobal(pos))

        if action == refresh_action:
            self.refresh_selected_item()
        # 处理选项的触发事件
        if action == delete_action:
            self.delete_selected_item()

    def delete_selected_item(self):
        # 删除当前选中的项
        current_item = self.list_widget.currentItem()
        # 删除数据
        execute_update_sql(f"update chats set is_del = 1 where types = '{current_item.text()}'", ())
        self.list_widget.takeItem(self.list_widget.row(current_item))

    def refresh_selected_item(self):
        # 刷新列表：查询数据库
        fields, self.rows = execute_query_sql("select * from chats where is_del = 0 or is_del = null group by types",
                                              ())
        rows_str = []
        for row in self.rows:
            rows_str.append(row[1])
        self.list_widget.clear()
        self.list_widget.addItems(rows_str)
        self.list_widget.currentItemChanged.connect(self.on_list_item_changed)

    # 按下enter按键之后调用
    def eventFilter(self, obj, event):
        if obj == self.text_edit_input and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Return and (
                    event.modifiers() == QtCore.Qt.AltModifier or event.modifiers() == QtCore.Qt.ControlModifier):
                # 按下 alt+Enter 进行的操作
                new_event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Enter, QtCore.Qt.NoModifier)
                QtWidgets.QApplication.postEvent(self.text_edit_input, new_event)
                return True
            elif event.key() == QtCore.Qt.Key_Return:
                # 按下 Enter 进行的操作
                self.send_message()
                return True
        return super().eventFilter(obj, event)
        # if obj == self.text_edit_input and event.type() == QtCore.QEvent.KeyPress:
        #     if event.key() == QtCore.Qt.Key_Return + QtCore.Qt.Key_Alt or event.key() == QtCore.Qt.Key_Enter + QtCore.Qt.Key_Alt:
        #         # 在这里执行自定义操作
        #         print("alt+Enter key pressed")
        #         # event.accept()  # 阻止默认的关闭事件
        #     elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
        #         # 在这里执行自定义操作
        #         print("Enter key pressed")
        #         # 在这里执行你想要的操作
        #         self.send_message()
        #         # event.accept()  # 阻止默认的关闭事件
        #         return True
        # return super().eventFilter(obj, event)

    # 弹出配置窗口
    def show_config_dialog(self):
        self.config_window.show()

    # 弹出语言配置窗口
    def show_language_dialog(self):
        self.language_window.show()

    # 加载完成后滚动到首页
    def on_load_finished(self):
        js_code = "window.scrollTo(0, document.body.scrollHeight);"
        self.web_view.page().runJavaScript(js_code)

    # 新增对话
    def send_text_add_button(self):
        global formatted_time
        formatted_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.list_widget.addItem(formatted_time)
        self.rows.append(list({1, formatted_time}))
        self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 点击左边的时间，右边的对话内容会相应的改变
    def on_list_item_changed(self, current_item):
        params["messages"] = []
        if current_item: self.on_list_item_changed_detail(current_item.text())

    def on_list_item_changed_detail(self, text):
        index = -1
        for item in self.rows:
            if item[1] == text: index = self.rows.index(item)
        self.selectRow = self.rows[index]
        global formatted_time
        formatted_time = self.selectRow[1]
        # 查询数据库中选择的对话
        fields, rows = execute_query_sql(f"select * from chats where types='{self.selectRow[1]}'", ())
        all_res[self.selectRow[1]] = ""
        all_res_root[self.selectRow[1]] = ""
        all_res_index[self.selectRow[1]] = len(rows) - 1
        for row in rows:
            indexs = rows.index(row)
            row2 = row[2]
            row3 = row[3]
            if row[2] is None: row2 = ""
            if row[3] is None: row3 = ""
            params["messages"].append({"role": "user", "content": row2})
            params["messages"].append({"role": "assistant", "content": row3})
            if row3.endswith("Goodbye!") or row3.endswith("再见！"):
                params["messages"] = []
            backgroundColor = "#343541"
            if indexs % 2 == 0: backgroundColor = "#444654"
            all_res_root[self.selectRow[1]] += f"""
问:
    {row2}
答:  
    {row3}



"""
            all_res[self.selectRow[1]] += f"""
<div style="background-color:{backgroundColor};padding: 10px;">
    <div>
        <span style="background-color: blueviolet;padding: 4px;">
            问:
        </span>    
        <pre style="background-color: darkslategray;padding:5px;border-radius: 10px;overflow: auto;word-break:break-all;white-space:pre-wrap;">{row2}</pre>
    </div>
    <div>
        <span style="background-color: darkgreen;padding: 4px;">
            答:
        </span>    
        <pre style="background-color: darkslategray;padding:5px;border-radius: 10px;overflow: auto;word-break:break-all;white-space:pre-wrap;">{row3}</pre>
    </div>
</div>
        """
        # 创建一个新线程来发送HTTP请求
        self.web_view.setHtml(self.get_text_html(all_res[self.selectRow[1]]))
        # self.text_edit_input1.setPlainText("".join(all_res_root[self.selectRow[1]]))
        # cursor = self.text_edit_input1.textCursor()
        # cursor.movePosition(QtGui.QTextCursor.End)
        # self.text_edit_input1.setTextCursor(cursor)
        # self.text_edit_input1.ensureCursorVisible()

    # Pygments语法高亮函数

    def get_text_html(self, text):
        try:
            # 解析markdown文本
            # html = markdown.markdown(text, extensions=['markdown.extensions.fenced_code'])
            html = text
            # 设置预览窗口的HTML内容和CSS样式表
            # 获取所有可用的样式
            all_styles = get_all_styles()
            all_css = []
            for style_name in all_styles:
                css = self.formatter.get_style_defs(style_name)
                all_css.append(css)

            all_css = '\n'.join(all_css)
            self.web_view.setStyleSheet(self.css + my_css + all_css)

            soup = BeautifulSoup(html, 'html.parser')
            code_tags = soup.find_all('code')
            for code_tag in code_tags:
                language = "python"
                try:
                    language = code_tag.get('class')[0][9:]  # 获取代码的语言
                except:
                    print("语言解析错误")
                code = code_tag.string  # 获取代码内容
                # 构造新的代码块 HTML
                new_code_tag = soup.new_tag("code", **{"class": f"language-{language}"})
                new_code_tag.string = highlight(code, language)
                # 替换原有的代码块 HTML
                code_tag.replace_with(new_code_tag)
            # 转换成字符串
            html = str(soup)
            res = html_top1 + self.css + my_css + html_top2 + htmls.unescape(html) + html_bottom
            # print(html)
            return res
        except:
            print("markdown解析报错了")

    def update_preview(self):
        self.web_view.setHtml(self.get_text_html(""))

    def send_message(self):
        # 获取用户输入的消息
        message = self.text_edit_input.toPlainText()
        # 创建一个新线程来发送HTTP请求
        thread = threading.Thread(target=self.send_http_request, args=(message,))
        thread.start()

    def send_http_request(self, message):
        # 创建并启动新线程来显示加载动画
        # 创建标签窗口和按钮窗口
        self.data_loading.emit(False)
        response = None
        res = None
        try:
            # 定义请求头
            headers = {
                'Content-type': 'application/json',
                'Authorization': f'Bearer {key}'
            }
            global params
            params["messages"].append({"role": "user", "content": message})
            # 将数据转换为JSON格式
            json_data = json.dumps(params)
            # 代理
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}",
            }
            if length:
                params["messages"] = params["messages"][(len(params["messages"]) - int(length)):len(params["messages"])]
            else:
                params = self.get_last_4096(0, message)
            # 发送HTTP请求
            try:
                json_data = json.dumps(params)
                response = requests.post(url, data=json_data, headers=headers, proxies=proxies)
                res = json.loads(response.text)
            except:
                try:
                    response = requests.post(url, data=json_data, headers=headers, )
                    res = json.loads(response.text)
                except Exception as err:
                    print(json.dumps(res))
                    self.data_error.emit(json.dumps(res))
            if res and 'error' in res and 'code' in res['error'] and res['error']['code'] == "context_length_exceeded":
                params["messages"] = []

            content = res['choices'][0]['message']['content']

            if content.endswith("Goodbye!") or content.endswith("再见！"):
                res['choices'][0]['message'] = []
            save_data_to_database(message, content, response.text)
            params["messages"].append({"role": "assistant", "content": content})
            # 发送数据到主线程
            self.data_ready.emit(f"{message}-|||-{content}")
        except Exception as err:
            print(json.dumps(res))
            self.data_error.emit(json.dumps(res))
        self.data_loading.emit(True)

    # 获取最后的4096个字节
    def get_last_4096(self, total_length, message):
        lens = len(json.dumps(params))
        array_length = len(params["messages"])
        if lens >= 4096:
            total_length += 1
            params["messages"] = params["messages"][total_length:array_length]
            return self.get_last_4096(total_length, message)
        else:
            return params

    @QtCore.pyqtSlot(str)
    def error_ui(self, message: str):
        QMessageBox.information(self, _("提示"), message)

    @QtCore.pyqtSlot(bool)
    def loading_ui(self, close: bool):
        if close:
            self.text_edit_button.setText("发送")
            self.text_edit_button.setDisabled(False)
            self.text_edit_input.installEventFilter(self)
        else:
            self.text_edit_button.setText("请求数据中...")
            self.text_edit_button.setDisabled(True)
            self.text_edit_input.removeEventFilter(self)
        self.repaint()

    @QtCore.pyqtSlot(str)
    def update_ui(self, message_content: str):
        message, content = message_content.split("-|||-")
        # 在主线程中更新 UI 元素
        # 将响应数据显示在聊天记录中
        backgroundColor = "#343541"
        if all_res_index[self.selectRow[1]] % 2 == 0: backgroundColor = "#444654"
        all_res_root[self.selectRow[1]] += f"""
        问:
            {message}
        答:  
            {content}



                """
        all_res[self.selectRow[1]] += f"""
        <div style="background-color:{backgroundColor};padding: 10px;">
            <div>
                <span style="background-color: blueviolet;padding: 4px;">
                    问:
                </span>    
                <pre style="background-color: darkslategray;padding:5px;border-radius: 10px;overflow: auto;word-break:break-all;white-space:pre-wrap;">{message}</pre>
            </div>
            <div>
                <span style="background-color: darkgreen;padding: 4px;">
                    答:
                </span>    
                <pre style="background-color: darkslategray;padding:5px;border-radius: 10px;overflow: auto;word-break:break-all;white-space:pre-wrap;">{content}</pre>
            </div>
        </div>
        """
        # 创建一个新线程来发送HTTP请求
        self.web_view.setHtml(self.get_text_html(all_res[self.selectRow[1]]))
        self.on_list_item_changed_detail(self.selectRow[1])
        # self.text_edit_input1.setPlainText("".join(all_res_root[self.selectRow[1]]))
        # cursor = self.text_edit_input1.textCursor()
        # cursor.movePosition(QtGui.QTextCursor.End)
        # self.text_edit_input1.setTextCursor(cursor)
        # self.text_edit_input1.ensureCursorVisible()
        self.text_edit_input.setPlainText("")
        self.repaint()


# 定义一个新线程
class LoadingThread(threading.Thread):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.stopped = False

    def run(self):
        # 加载动画文件
        movie = QMovie('loading.gif')
        self.label.setMovie(movie)

        # 启动动画
        movie.start()

        # 线程不停止时，保持动画运行
        while not self.stopped:
            sleep(0.1)

        # 停止动画并清除标签上的内容
        movie.stop()
        self.label.clear()
