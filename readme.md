# A virtual book library using PyQt5

### Note
First run of the app takes longer, as it scrapes and stores books for the first time

### Description
This project is divided into few parts:

"main.py" is responsible to import necessary modules and run the app.

In modules folder I have "users.py", which is responsible handling user registration and login.

"database.py" is a database manager with common CRUD methods.

And "library.py" module contains features to read books from DB, to display them in GUI, add and remove favorite books.

To access the library, the user must register and then log in.


### Requirements
- Python 3.x (3.9 recommended)
- PyQt5==5.15.9
- pandas==2.2.1

to install required packages run in terminal: pip install -requirements.txt
