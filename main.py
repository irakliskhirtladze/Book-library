import sys
import json
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QIcon
from modules.users import Register, Login
from modules.library import Library


def reset_current_events() -> None:
    with open("utils/current_user.json", "w") as json_file:
        json.dump({"email": ""}, json_file, indent=4)

    with open("utils/current_table.json", "w") as json_file:
        json.dump({"current_table": ""}, json_file, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QStackedWidget()

    regWindow = Register(widget)
    logWindow = Login(widget)
    libWindow = Library(widget)
    widget.addWidget(logWindow)
    widget.addWidget(regWindow)
    widget.addWidget(libWindow)

    widget.setWindowTitle("Library")
    widget.setWindowIcon(QIcon("assets/books.png"))
    widget.show()

    app.aboutToQuit.connect(reset_current_events)

    sys.exit(app.exec_())
