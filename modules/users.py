import sqlite3
import hashlib
import json
from modules.database import DatabaseManager
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


def hash_password(password) -> str:
    """Returns encrypted password"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(entered_password, stored_password) -> bool:
    """Returns Boolean value of password validity"""
    return hash_password(entered_password) == stored_password


def read_users_table() -> dict:
    """Opens and extracts data from users table"""
    db_manager = DatabaseManager('LIBRARY.db')
    rows = db_manager.load_data('users')
    return {row[0]: row[1] for row in rows}


class Register(QMainWindow):
    """A class to let user register in the system"""

    def __init__(self, widget) -> None:
        super().__init__()

        # Set up the user interface from Designer
        self.reg_ui = loadUi("ui/reg.ui", self)
        self.widget = widget

        self.db_manager = DatabaseManager('LIBRARY.db')

        # Connects buttons with screen switcher and registration methods
        self.reg_ui.pushButton_2.clicked.connect(self.switch_to_login)
        self.reg_ui.pushButton.clicked.connect(self.register)

    def switch_to_login(self) -> None:
        """Allows a user to switch to login screen"""
        self.widget.setCurrentIndex(0)

        # Clears the info label when switching window
        self.reg_ui.label_4.setStyleSheet("color: transparent; background-color:transparent")
        self.reg_ui.label_4.setText("")

    def register(self) -> None:
        """Checks for user input and if validated, writes credentials to DB.
        """
        email_rows = self.db_manager.search('users', ['email'])
        emails_in_db = [row[0] for row in email_rows]

        # Reads user input
        email = self.reg_ui.lineEdit.text()
        password = self.reg_ui.lineEdit_2.text()

        # Control flow depending on registration rules
        if email in emails_in_db:
            self.reg_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.reg_ui.label_4.setText("This email is already registered")

        elif "@" not in email:
            self.reg_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.reg_ui.label_4.setText("Invalid email")

        elif len(password) < 4:
            self.reg_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.reg_ui.label_4.setText("Password must be at least 4 characters")

        else:
            try:  # Writing to DB can fail when it's used concurrently
                hashed_password = hash_password(password)
                self.db_manager.add_record('users', email, hashed_password)

                self.reg_ui.label_4.setStyleSheet("color: green; background-color:transparent")
                self.reg_ui.label_4.setText("Registration successful!")

            except sqlite3.OperationalError:
                self.reg_ui.label_4.setStyleSheet("color: red; background-color:transparent")
                self.reg_ui.label_4.setText("Could not save to database. Close if it is open!")


class Login(QMainWindow):
    """A class to handle user login"""

    def __init__(self, widget) -> None:
        super().__init__()

        # Set up the user interface from Designer
        self.log_ui = loadUi("ui/login.ui", self)
        self.widget = widget

        self.log_ui.pushButton_2.clicked.connect(self.switch_to_register)
        self.log_ui.pushButton.clicked.connect(self.login)

    def switch_to_register(self) -> None:
        """Allows a user to switch to registration screen"""
        self.widget.setCurrentIndex(1)

        # Clears the info label when switching window
        self.log_ui.label_4.setStyleSheet("color: transparent; background-color:transparent")
        self.log_ui.label_4.setText("")

    def login(self) -> None:
        """Lets user login to system if registered"""

        # Reads user input
        email = self.log_ui.lineEdit.text()
        password = self.log_ui.lineEdit_2.text()

        # Checks login rules and tries to login
        if email not in read_users_table():
            self.log_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.log_ui.label_4.setText("No such email found!")

        elif not check_password(password, read_users_table()[email]):
            self.log_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.log_ui.label_4.setText("Password is incorrect!")

        else:
            try:
                # Writes logged-in user to json file to be read by Library class
                with open('utils/current_user.json', 'w') as file:
                    json.dump({'email': email}, file, indent=4)

                # Switches active widget to library
                self.widget.setCurrentIndex(2)
                # Clears the info label when switching window
                self.log_ui.lineEdit.clear()
                self.log_ui.lineEdit_2.clear()

            except Exception as e:
                print(e)
