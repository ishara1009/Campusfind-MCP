from contextlib import contextmanager
from typing import Iterator

import mysql.connector
from mysql.connector import MySQLConnection

from app.config import get_settings


def connect_to_database() -> MySQLConnection:
    settings = get_settings()
    return mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        charset="utf8mb4",
        use_unicode=True,
        connection_timeout=10,
    )


@contextmanager
def database_connection() -> Iterator[MySQLConnection]:
    connection = connect_to_database()
    try:
        yield connection
    finally:
        if connection.is_connected():
            connection.close()
