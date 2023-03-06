import sys

from PyQt5.QtWidgets import QApplication

from libs.MyMainWindow import MyMainWindow
from libs.SqlUtils import create_data_base

if __name__ == "__main__":
    print("start")
    create_data_base()
    app = QApplication(sys.argv)

    main_window = MyMainWindow()
    main_window.show()

    sys.exit(app.exec_())
