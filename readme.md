# A Virtual Book Library using PyQt5
## Note
Please be aware that the initial run of the application may take longer as it scrapes and stores books for the first time.

## Description
This project is divided into several parts:

- main.py: Responsible for importing necessary modules and running the application.

- modules/users.py: Handles user registration and login.

- modules/database.py: Manages the database with common CRUD methods.

- modules/library.py: Contains features to read books from the database, display them in the GUI, and add or remove favorite books.

- Access to the library requires user registration followed by login.

## Requirements
- Python 3.x (3.9 recommended)
- PyQt5==5.15.9
- pandas==1.2.2

To install the required packages, run the following command in the terminal:

```` bash
pip install -r requirements.txt
````
