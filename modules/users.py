import sqlite3
import hashlib
import json
from modules.database import create_users_table, table_exists
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


def hash_password(password) -> str:
    """Returns encrypted password"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(entered_password, stored_password) -> bool:
    """Returns Boolean value of password validity"""
    return hash_password(entered_password) == stored_password


def read_db() -> dict:
    """Opens and extracts data from database"""
    conn = sqlite3.connect("LIBRARY.db")
    curs = conn.cursor()
    curs.execute("SELECT * FROM users")
    rows = curs.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


class Register(QMainWindow):
    """A class to let user register in the system"""

    def __init__(self, widget) -> None:
        super().__init__()

        # Set up the user interface from Designer
        self.reg_ui = loadUi("ui/reg.ui", self)
        self.widget = widget

        if not table_exists('users'):
            create_users_table()

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
        """Gets a database ready.
        Then checks for user input and tries to write credentials to DB.
        """
        conn = sqlite3.connect('LIBRARY.db')
        curs = conn.cursor()
        curs.execute("SELECT email FROM users")
        rows = curs.fetchall()
        emails_in_db = [row[0] for row in rows]

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
                curs.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
                conn.commit()
                self.reg_ui.label_4.setStyleSheet("color: green; background-color:transparent")
                self.reg_ui.label_4.setText("Registration successful!")
                conn.close()
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
        if email not in read_db():
            self.log_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.log_ui.label_4.setText("No such email found!")
        elif not check_password(password, read_db()[email]):
            self.log_ui.label_4.setStyleSheet("color: red; background-color:transparent")
            self.log_ui.label_4.setText("Password is incorrect!")
        else:
            try:
                # Writes logged in user to json file to be read by Library class
                with open('active_user.json', 'w') as file:
                    json.dump({'email': email}, file, indent=4)

                # Switches active widget to library
                self.widget.setCurrentIndex(2)
                # Clears the info label when switching window
                self.log_ui.lineEdit.clear()
                self.log_ui.lineEdit_2.clear()

            except Exception as e:
                print(e)
