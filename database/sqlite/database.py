
import os
from typing import Dict, List, Tuple

import sqlite3

class SQLite:
    def __init__(self):
        self.connection = sqlite3.connect(os.path.join("db_store", "finance.db"))
        self.cursor = self.connection.cursor()

    def insert(self, table: str, column_values: Dict):
        columns = ', '.join(column_values.keys())
        values = [tuple(column_values.values())]
        placeholders = ", ".join("?" * len(column_values.keys()))

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        self.cursor.executemany(query, values)
        self.cursor.commit()

    def fetch_all(self, table: str, columns: List[str]) -> List[Tuple]:
        columns_joined = ", ".join(columns)

        self.cursor.execute(f"SELECT {columns_joined} FROM {table}")

        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            dict_row = {}
            for index, column in enumerate(columns):
                dict_row[column] = row[index]
            result.append(dict_row)

        return result

    def delete(self, table: str, row_id: int) -> None:
        row_id = int(row_id)

        self.cursor.execute(f"delete from {table} where id={row_id}")
        self.connection.commit()

    def get_cursor(self, ):
        return self.cursor

    def _init_db(self, ):
        with open(os.path.join("utils", "sql", "finance.db")) as f:
            sql = f.read()

        self.cursor.executescript(sql)
        self.connection.commit()

    def check_db_exists(self):
        self.cursor.execute("SELECT name FROM sqlite_master "
                       "WHERE type='table' AND name='expense'")

        table_exists = self.cursor.fetchall()
        if table_exists:
            return

        self._init_db()