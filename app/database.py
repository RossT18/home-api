from fastapi import Depends
from dotenv import load_dotenv
import os
import sqlite3
from typing import Generator, Annotated


load_dotenv()

database_path = os.getenv("DATABASE_PATH", "database.db")


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependency that yields a per-request SQLite connection.
    row_factory lets route handlers access columns by name instead of index.
    The connection is always closed when the request finishes.
    """
    conn = sqlite3.connect(database_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn # Give connection to route handler
    finally:
        # Close connection after the request is finished
        conn.close()


DatabaseConnectionDep = Annotated[sqlite3.Connection, Depends(get_db)]
