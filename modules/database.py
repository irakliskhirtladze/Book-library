import sqlite3
import random
import pandas as pd


def table_exists(table_name):
    """Returns boolean value based on existence of table in DB"""
    conn = sqlite3.connect('LIBRARY.db')
    curs = conn.cursor()
    curs.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    result = curs.fetchone()
    conn.close()
    return result is not None


def create_users_table():
    """ Establish DB connection and create table if not yet present """
    # Establish a connection with database
    conn = sqlite3.connect('LIBRARY.db')
    curs = conn.cursor()
    curs.execute(
        """CREATE TABLE IF NOT EXISTS "users" (
        "email" TEXT PRIMARY KEY NOT NULL,
        "password" TEXT NOT NULL
        )""")
    conn.close()


def scrape_books():
    """ Scrapes books from 'goodreads.com' and stores them to database"""
    # Establish a connection with database
    conn = sqlite3.connect('LIBRARY.db')
    curs = conn.cursor()
    curs.execute(
        """CREATE TABLE IF NOT EXISTS "books" (
        "book_id" INTEGER PRIMARY KEY NOT NULL,
        "name" TEXT NOT NULL,
        "author" TEXT,
        "num_pages" INTEGER,
        "cover_type" TEXT,
        "category" TEXT
        )
        """
    )

    urls = {'fantasy': 'https://www.goodreads.com/list/show/50.The_Best_Epic_Fantasy_fiction_',
            'sci-fi': 'https://www.goodreads.com/list/show/4893.Best_Science_Fiction_of_the_21st_Century',
            'horror': 'https://www.goodreads.com/list/show/135.Best_Horror_Novels',
            'thriller': 'https://www.goodreads.com/list/show/73283.100_Mysteries_and_Thrillers_to_Read_in_a_Lifetime_Readers_Picks'
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
    full_df.insert(0, 'book_id', [id for id in range(len(full_df))])
    full_df.drop_duplicates(subset=['name', 'author'], keep='first', inplace=True)

    full_df.to_sql('books', conn, if_exists='append', index=False)
    conn.close()
