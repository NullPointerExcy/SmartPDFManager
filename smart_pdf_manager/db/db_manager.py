import os
import sqlite3
from typing import Dict


class DBManager:
    __connection = None

    @property
    def connection(self):
        return self.__connection

    def __init__(self):
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database and create the table if it doesn't exist."""
        if not os.path.exists('db'):
            os.makedirs('db')
        self.__connection = sqlite3.connect('db/spdfm.db')
        cursor = self.__connection.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS label_value (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL
                )
            ''')
        self.__connection.commit()

    def load_labels_from_db(self) -> Dict[str, str]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT key, value FROM label_value")
        rows = cursor.fetchall()

        label_dict = {key: value for key, value in rows}
        return label_dict

    def select_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT key, value FROM label_value")
        return cursor.fetchall()

    def insert_label(self, key, value):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO label_value(key, value) VALUES (?, ?)", (key, value))
        self.connection.commit()
        return cursor.lastrowid

    def update_label(self, old_key, new_key, new_value):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE label_value SET key = ?, value = ? WHERE key = ?", (new_key, new_value, old_key))
        self.connection.commit()

    def delete_label(self, key):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM label_value WHERE key = ?", (key,))
        self.connection.commit()

    def get_count(self, new_key):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM label_value WHERE key = ?", (new_key, ))
        return cursor.fetchone()[0]

    def close_connection(self):
        if self.__connection:
            self.__connection.close()
