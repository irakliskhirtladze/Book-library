import sqlite3
import json
import random
import pandas as pd
from modules.database import DatabaseManager
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.uic import loadUi


def scrape_books() -> None:
    """ Scrapes books from 'goodreads.com' and stores them to database"""

    urls = {
        'fantasy': 'https://www.goodreads.com/list/show/50.The_Best_Epic_Fantasy_fiction_',
        'sci-fi': 'https://www.goodreads.com/list/show/4893.Best_Science_Fiction_of_the_21st_Century',
        'horror': 'https://www.goodreads.com/list/show/135.Best_Horror_Novels',
        'thriller': 'https://www.goodreads.com/list/show/73283'
                    '.100_Mysteries_and_Thrillers_to_Read_in_a_Lifetime_Readers_Picks'
    }

    covers = ['Hardback', 'Paperback', 'Softcover']
    dfs = []  # Stores pandas dataframes from different webpages
    # Iterate over URLs and get books from them using pandas
    for category, url in urls.items():
        df = pd.read_html(url)[0]
        df['name'] = df[2].apply(lambda x: x.split('by')[0])
        df['author'] = df[2].apply(lambda x: x.split('by')[1])
        df['author'] = df['author'].str.split(r'\(|\d', expand=True)[0]
        df['num_pages'] = [random.randint(300, 900) for _ in range(len(df))]
        df['cover_type'] = [random.choice(covers) for _ in range(len(df))]
        df['category'] = [category for _ in range(len(df))]

        df = df[['name', 'author', 'num_pages', 'cover_type', 'category']]
        dfs.append(df)

    # Concatenate dataframes into single dataframe and save to database
    full_df = pd.concat(dfs, axis=0)
    book_ids = [book_id for book_id in range(1, len(full_df) + 1)]
    full_df.insert(0, 'book_id', book_ids)
    full_df.drop_duplicates(subset=['name', 'author'], keep='first', inplace=True)

    # Save to database
    db_manager = DatabaseManager('LIBRARY.db')
    with db_manager.create_connection() as conn:
        full_df.to_sql('books', conn, if_exists='append', index=False)


def get_current_item(file_name: str, item_name: str) -> str:
    """Returns current user email"""
    with open(file_name, 'r') as file:
        return json.load(file)[item_name]


def clear_label(labels: list) -> None:
    """Clears text from given list of labels"""
    for label in labels:
        label.setStyleSheet("background-color:transparent")
        label.setText("")


def populate_book_table(data, widget) -> None:
    """Populates table with books"""
    column_names = ['Book ID', 'Name', 'Author', 'Page count', 'Cover type', 'Category']
    widget.setRowCount(len(data))
    widget.setColumnCount(len(data[0]))

    # Populate the table with the fetched data
    for row_num, row_data in enumerate(data):
        for col_num, cell_data in enumerate(row_data):
            item = QTableWidgetItem(str(cell_data))
            widget.setItem(row_num, col_num, item)


def get_selected_rows_from_table(widget, columns) -> list:
    """Returns list of selected rows from table"""
    column_count = len(columns)
    selected_rows = []
    for current in widget.selectionModel().selectedRows():
        row = []
        for column in range(column_count):
            item = widget.item(current.row(), column)
            if item is not None:
                row.append(item.text())
            else:
                row.append('')  # Append empty string if item is None
        selected_rows.append(tuple(row))
    return selected_rows


class Library(QMainWindow):
    """A class to manage a virtual library of books"""

    def __init__(self, widget) -> None:
        super().__init__()

        self.db_manager = DatabaseManager('LIBRARY.db')
        self.db_manager.create_tables()
        if self.db_manager.is_table_empty('books'):
            scrape_books()

        # Set up the user interface from Designer
        self.lib_ui = loadUi("ui/library.ui", self)
        self.widget = widget

        self.lib_ui.pushButton.clicked.connect(self.logout)
        self.lib_ui.pushButton_3.clicked.connect(self.show_all_books)
        self.lib_ui.pushButton_2.clicked.connect(self.add_to_favorites)
        self.lib_ui.pushButton_4.clicked.connect(self.show_favorites)
        self.lib_ui.pushButton_5.clicked.connect(self.delete_from_favorites)

        # Set the background color of the header row and column to transparent
        header_style = """QHeaderView::section { background-color: lightblue; }"""
        self.lib_ui.tableWidget.horizontalHeader().setStyleSheet(header_style)
        self.lib_ui.tableWidget.verticalHeader().setStyleSheet(header_style)

    def showEvent(self, event) -> None:
        """Shows currently active user's email label on library page"""
        super().showEvent(event)
        if self.widget.currentIndex() == 2:
            self.lib_ui.label_5.setText(f"Logged in as: {get_current_item('utils/current_user.json', 'email')}")

    def logout(self) -> None:
        """Allows a user to log out and return to login screen"""
        self.widget.setCurrentIndex(0)

        with open('utils/current_user.json', 'w') as file:
            json.dump({'email': ""}, file, indent=4)

        # Clears the info label when switching window
        clear_label([self.lib_ui.label_3, self.lib_ui.label_5, self.lib_ui.label_6, self.lib_ui.label_7])
        # Clears the table of all books
        self.lib_ui.tableWidget.clearContents()
        self.lib_ui.tableWidget.setRowCount(0)

    def show_all_books(self) -> None:
        """Reads DB and displays all books from it"""
        data = self.db_manager.load_data('books')

        populate_book_table(data, self.lib_ui.tableWidget)

        self.lib_ui.label_3.setText(f"Showing all books. Total books: {len(data)}")

        with open('utils/current_table.json', 'w') as file:
            json.dump({'current_table': 'all_books'}, file, indent=4)

    def add_to_favorites(self) -> None:
        """Adds selected books to user's favorites"""
        # Getting selected rows from the tableWidget
        selected_rows = get_selected_rows_from_table(self.lib_ui.tableWidget, self.db_manager.get_columns('books'))

        # Read currently logged-in user
        email = get_current_item('utils/current_user.json', 'email')

        # Add selected rows to user's favorites
        for row in selected_rows:
            try:
                self.db_manager.add_record('favorites', email, int(row[0]))
            except sqlite3.IntegrityError:
                pass

    def show_favorites(self) -> None:
        """Shows list of user's favorite books"""
        query = """
            SELECT b.book_id, b.name, b.author, b.num_pages, b.cover_type, b.category
            FROM books b JOIN favorites f ON b.book_id = f.book_id
            WHERE f.email = ?
            """

        email = get_current_item('utils/current_user.json', 'email')
        with self.db_manager.create_connection() as conn:
            curs = conn.cursor()
            curs.execute(query, (email,))
            data = curs.fetchall()

        populate_book_table(data, self.lib_ui.tableWidget)

        with open('utils/current_table.json', 'w') as file:
            json.dump({'current_table': 'favorite_books'}, file, indent=4)

        self.lib_ui.label_3.setText(f"Showing favorites. You have {len(data)} favorite books")

    def delete_from_favorites(self) -> None:
        """Deletes selected books from user's favorites"""
        # Read currently displayed table
        current_table = get_current_item('utils/current_table.json', 'current_table')

        if current_table == 'favorite_books':
            # Removing selected books from user's favorites
            selected_rows = get_selected_rows_from_table(self.lib_ui.tableWidget, self.db_manager.get_columns('books'))
            for row in selected_rows:
                self.db_manager.delete_row_by_key('favorites', 'book_id', int(row[0]))

            self.lib_ui.label_4.setStyleSheet("color: green; background-color: transparent")
            self.lib_ui.label_4.setText("Removed selected books from favorites")

            # Refresh the table of favorite books
            if selected_rows:
                self.show_favorites()

            else:
                self.lib_ui.label_4.setStyleSheet("color: red; background-color: transparent")
                self.lib_ui.label_4.setText("No books selected to be removed")

        else:
            self.lib_ui.label_4.setStyleSheet("color: red; background-color: transparent")
            self.lib_ui.label_4.setText("No books selected to be removed")
