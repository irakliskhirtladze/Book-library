# A virtual book library using PyQt5

### Note 
The "scrape_books.py" file is optional.
It was used initially to scrape books from goodreads.com and is not required for the app to work.

### Description
This project is divided into few parts:
LIBRARY.db has 2 tables: users and books.
Users table is hosting the user credentials upon registration.
Books in "books" table were inserted by using "scrape_books.py".

"main.py" is responsible to import necessary modules and run the app.

In modules folder I have "users.py" from previous project, with few modifications, which is responsible
for handling user registration and login.

And a new - "library.py" module contains few functionalities to read books from DB, to display them in GUI,
etc.

To access the library, the user must register and then log in.
On the library page, the Two buttons on the bottom are used to obtain average number of pages in whole library
and tho obtain the name of the largest book.

"active_user.json" is used to store user mail information temporarily upon login.
This is used to display current user's email on the library page of the app.
In the future I might add user's name, last name and more info to the file for other purposes.

### Requirements
Python 3.x (3.9 recommended)

PyQt5

Pandas and lxml only for "scrape_books.py"
