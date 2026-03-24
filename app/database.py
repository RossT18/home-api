from fastapi import Depends
from dotenv import load_dotenv
import os
import sqlite3
from typing import Generator, Annotated


load_dotenv()

database_path = os.getenv('DATABASE_PATH', 'database.db')

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependency that yields a per-request SQLite connection.
    row_factory lets route handlers access columns by name instead of index.
    The connection is always closed when the request finishes.
    """
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

DatabaseConnectionDep = Annotated[sqlite3.Connection, Depends(get_db)]
