from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QShortcut, QInputDialog


class WebSearchPage(QWebEnginePage):
    def __init__(self, parent=None):
        super(WebSearchPage, self).__init__(parent)
        self.highlight_results = []
        self.highlight_index = 0

    def findText(self, text, options=QWebEnginePage.FindFlags()):
        if not text:
            return False

        if options & QWebEnginePage.FindBackward:
            self.highlight_index -= 1
        else:
            self.highlight_index += 1

        self.findText(text, options, self.process_search_result)
        return bool(self.highlight_results)

    def process_search_result(self, result):
        self.highlight_results = result
        self.highlight_index %= len(self.highlight_results)
        self.highlightSelectedText()

    def highlightSelectedText(self):
        for match in self.highlight_results:
            self.runJavaScript(
                f"var sel = window.getSelection();"
                f"var range = document.createRange();"
                f"range.setStart({{node:sel.anchorNode, offset:sel.anchorOffset}});"
                f"range.setEnd({{node:sel.focusNode, offset:sel.focusOffset}});"
                f"sel.removeAllRanges();"
                f"sel.addRange(range);"
                f"var element = document.createElement(\"span\");"
                f"element.style.backgroundColor = \"yellow\";"
                f"range.surroundContents(element);",
                self.remove_highlight
            )

    def remove_highlight(self, _):
        for match in self.highlight_results:
            self.runJavaScript(
                "var element = document.querySelector('span[style=\"background-color: yellow;\"]');"
                "if (element) {"
                "    var parent = element.parentNode;"
                "    parent.insertBefore(document.createTextNode(element.textContent), element);"
                "    parent.removeChild(element);"
                "}",
                self.finish_processing_search_result
            )

    def finish_processing_search_result(self, _):
        self.highlight_results.clear()
        self.highlight_index %= len(self.highlight_results)


class WebSearchWidget(QWidget):
    def __init__(self, parent=None):
        super(WebSearchWidget, self).__init__(parent)
        self.web_view = QWebEngineView()
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.web_view)

        self.search_page = WebSearchPage(self)
        self.web_view.setPage(self.search_page)
        self.web_view.load("https://www.google.com")

        # Connect Ctrl + F key event to search
        self.shortcut = QShortcut(Qt.CTRL + Qt.Key_F, self.web_view)
        self.shortcut.activated.connect(self.show_search_dialog)


def show():
    widget = WebSearchWidget()
    widget.show()