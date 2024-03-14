import sys
import json
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QIcon
from modules.users import Register, Login
from modules.library import Library


def save_user_logged_in() -> None:
    with open("active_user.json", "w") as json_file:
        json.dump({"email": ""}, json_file, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QStackedWidget()

    regWindow = Register(widget)
    logWindow = Login(widget)
    libWindow = Library(widget)
    widget.addWidget(logWindow)
    widget.addWidget(regWindow)
    widget.addWidget(libWindow)

    widget.setWindowTitle("TBC Academy")
    widget.setWindowIcon(QIcon("assets/books.png"))
    widget.show()

    app.aboutToQuit.connect(save_user_logged_in)

    sys.exit(app.exec_())
