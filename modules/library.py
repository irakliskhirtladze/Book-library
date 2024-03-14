import sqlite3
import json
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from PyQt5.uic import loadUi


def clear_label(labels: list) -> None:
    """Clears text from given list of labels"""
    for label in labels:
        label.setStyleSheet("background-color:transparent")
        label.setText("")


class Library(QMainWindow):
    """A class to manage a virtual library of books"""

    def __init__(self, widget) -> None:
        super().__init__()

        # Set up the user interface from Designer
        self.lib_ui = loadUi("ui/library.ui", self)
        self.widget = widget
        
        self.lib_ui.pushButton.clicked.connect(self.logout)
        self.lib_ui.pushButton_3.clicked.connect(self.show_all_books)
        self.lib_ui.pushButton_2.clicked.connect(self.show_average_page_num)
        self.lib_ui.pushButton_4.clicked.connect(self.show_largest_book)

    def showEvent(self, event) -> None:
        """Shows currently active user's email label on library page"""
        super().showEvent(event)
        if self.widget.currentIndex() == 2:
            with open('active_user.json', 'r') as file:
                self.lib_ui.label_5.setText(f"Logged in as: {json.load(file)['email']}")
            
    def logout(self) -> None:
        """Allows a user to log out and return to login screen"""
        self.widget.setCurrentIndex(0)

        with open('active_user.json', 'w') as file:
            json.dump({'email':""}, file, indent=4)

        # Clears the info label when switching window
        clear_label([self.lib_ui.label_5, self.lib_ui.label_6, self.lib_ui.label_7])
        # Clears the table of all books
        model = QSqlQueryModel()
        self.lib_ui.tableView.setModel(model)

    def show_all_books(self) -> None:
        """Reads DB and displays all books from it"""
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('LIBRARY.db')

        # "self.db.open()" line attempt to open db and returns True if successul
        if not self.db.open():
            return   
              
        query = QSqlQueryModel()
        query.setQuery("SELECT * FROM books")
        self.tableView.setModel(query)

        self.tableView.horizontalHeader().setStyleSheet("background-color: transparent")
        self.tableView.verticalHeader().setStyleSheet("QHeaderView::section { background-color: transparent; }")

    def show_average_page_num(self) -> None:
        """Shows average number of pages in the entire library"""
        conn = sqlite3.connect('LIBRARY.db')
        curs = conn.cursor()
        curs.execute("SELECT AVG(num_pages) FROM books")
        self.lib_ui.label_6.setText(f"{round(curs.fetchone()[0])}")
        conn.close()

    def show_largest_book(self) -> None:
        """Shows the name of the largest book in the entire library"""
        conn = sqlite3.connect('LIBRARY.db')
        curs = conn.cursor()
        curs.execute("SELECT name FROM books WHERE num_pages = (SELECT MAX(num_pages) FROM books)")
        self.lib_ui.label_7.setText(f"{curs.fetchone()[0]} + ")
        conn.close()
        
        
