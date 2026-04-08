import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


DB_PATH = Path("db/checkpoints.db")


def build_checkpointer():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return checkpointer
