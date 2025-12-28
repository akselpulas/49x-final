"""
Database configuration and connection management for CE49X Final Project.
Supports PostgreSQL via psycopg2 or asyncpg.
"""

import os
from pathlib import Path
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'ce49x_db'),
    'user': os.getenv('DB_USER', 'ce49x_user'),
    'password': os.getenv('DB_PASSWORD', 'ce49x_password'),
}

# Connection pool
_pool: Optional[SimpleConnectionPool] = None


def init_pool(minconn=1, maxconn=10):
    """Initialize connection pool."""
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            **DB_CONFIG
        )
    return _pool


def get_connection():
    """Get a connection from the pool."""
    if _pool is None:
        init_pool()
    return _pool.getconn()


def return_connection(conn):
    """Return a connection to the pool."""
    if _pool:
        _pool.putconn(conn)


@contextmanager
def get_db_cursor(dict_cursor=True):
    """
    Context manager for database operations.
    
    Usage:
        with get_db_cursor() as cur:
            cur.execute("SELECT * FROM articles")
            results = cur.fetchall()
    """
    conn = get_connection()
    try:
        if dict_cursor:
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        return_connection(conn)


def test_connection() -> bool:
    """Test database connection."""
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


def close_pool():
    """Close all connections in the pool."""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None

