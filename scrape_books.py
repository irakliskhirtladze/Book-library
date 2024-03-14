import sqlite3
import random
import pandas as pd


def connect_db():
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
    return None


def scrape_books():
    urls = {'fantasy': 'https://www.goodreads.com/list/show/50.The_Best_Epic_Fantasy_fiction_',
            'sci-fi': 'https://www.goodreads.com/list/show/4893.Best_Science_Fiction_of_the_21st_Century',
            'horror': 'https://www.goodreads.com/list/show/135.Best_Horror_Novels',
            'thriller': 'https://www.goodreads.com/list/show/73283.100_Mysteries_and_Thrillers_to_Read_in_a_Lifetime_Readers_Picks'
            }

    covers = ['Hardback', 'Paperback', 'Softcover']
    dfs = []
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

    full_df = pd.concat(dfs, axis=0)
    full_df.insert(0, 'book_id', [id for id in range(len(full_df))])
    full_df.drop_duplicates(subset=['name', 'author'], keep='first', inplace=True)

    return full_df


def write_to_db(df):
    conn = sqlite3.connect('LIBRARY.db')
    df.to_sql('books', conn, if_exists='append', index=False)
    conn.close()


if __name__ == "__main__":
    connect_db()
    write_to_db(scrape_books())
