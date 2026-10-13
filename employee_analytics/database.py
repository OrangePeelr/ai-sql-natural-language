"""Reproducible seed data and restricted SQLite query execution."""
from pathlib import Path
from contextlib import closing
import sqlite3
import time

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
DB_PATH = DATA_DIR / 'employees.db'


def initialize(path=DB_PATH):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f'{path.name} already exists; choose a new path to rebuild.')
    with closing(sqlite3.connect(path)) as conn:
        with conn:
            conn.executescript((DATA_DIR / 'schema.sql').read_text())
            conn.executescript((DATA_DIR / 'seed.sql').read_text())
            assert not conn.execute('PRAGMA foreign_key_check').fetchall()


def query(sql, path=DB_PATH, max_rows=200):
    """Allow reads of employee only; bound execution time and returned rows."""
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)) as conn:
        conn.execute('PRAGMA query_only = ON')
        def authorize(action, table, column, db, trigger):
            if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and table == 'employee':
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and column != 'load_extension':
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY
        conn.set_authorizer(authorize)
        deadline = time.monotonic() + 3
        conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        cursor = conn.execute(sql)
        if cursor.description is None:
            raise ValueError('Expected a query returning rows.')
        rows = cursor.fetchmany(max_rows + 1)
        return {'columns': [c[0] for c in cursor.description],
                'rows': [list(r) for r in rows[:max_rows]],
                'truncated': len(rows) > max_rows}


if __name__ == '__main__':
    initialize()
    print('Created data/employees.db with 30 employees.')

