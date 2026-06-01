"""DB compatibility shim.

When `DATABASE_URL` is unset → sqlite at sessions.db (local dev).
When `DATABASE_URL` is set to a Postgres URL → Supabase / Render Postgres.

The shim exposes the same surface webapp.py was using on raw sqlite3
(`_db()` returning a connection that supports `execute(sql, params)` with
`?` placeholders, rows accessible by column name, and `IntegrityError`).
The only awkward bit is `PRAGMA table_info(...)` which has no Postgres
equivalent — see `column_names(conn, table)` below.
"""
from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
SQLITE_PATH = HERE / "sessions.db"

_RAW_URL = (os.environ.get("DATABASE_URL") or "").strip()
USE_POSTGRES = _RAW_URL.startswith(("postgres://", "postgresql://"))

if USE_POSTGRES:
    # psycopg2 wants 'postgresql://'
    if _RAW_URL.startswith("postgres://"):
        _RAW_URL = "postgresql://" + _RAW_URL[len("postgres://"):]
    import psycopg2  # noqa: F401  (also used in is_duplicate_column_error)
    import psycopg2.extras
    from psycopg2 import pool as _pg_pool

    _POOL = _pg_pool.ThreadedConnectionPool(1, 6, dsn=_RAW_URL)


# ── Sqlite-compatible exception alias ────────────────────────────────────
if USE_POSTGRES:
    class IntegrityError(Exception):
        pass
else:
    IntegrityError = sqlite3.IntegrityError  # type: ignore[misc]


def _to_pg_sql(sql: str) -> str:
    """Translate sqlite-flavoured SQL → postgres."""
    # Placeholder: ? → %s. Our queries don't have ? inside string literals, so
    # the naive replace is safe.
    sql = sql.replace("?", "%s")
    # AUTOINCREMENT → SERIAL
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    # IMPORTANT: postgres REAL is 4-byte single precision (~7 significant digits)
    # while sqlite REAL is 8-byte double. time.time() = 1.7e9 has 10+ digits
    # before the decimal, so single-precision REAL would round to the nearest
    # few seconds — silent corruption of timestamps. Force DOUBLE PRECISION.
    sql = re.sub(r"\bREAL\b", "DOUBLE PRECISION", sql)
    # `excluded.col` works in postgres ON CONFLICT, no change needed.
    # CREATE INDEX IF NOT EXISTS — supported in both.
    # COALESCE — same in both.
    return sql


class _Cursor:
    """Wraps a DB-API cursor; lets fetchone()/fetchall() return rows that the
    existing code already understands."""
    def __init__(self, raw):
        self._raw = raw

    def fetchone(self):
        return self._raw.fetchone()

    def fetchall(self):
        return self._raw.fetchall()

    @property
    def lastrowid(self):
        return getattr(self._raw, "lastrowid", None)

    def close(self):
        try:
            self._raw.close()
        except Exception:
            pass


class _Conn:
    """sqlite-compatible context-manager wrapper around a real connection."""
    def __init__(self, raw, kind):
        self._raw = raw
        self._kind = kind  # 'sqlite' | 'postgres'

    def execute(self, sql, params=()):
        if self._kind == "postgres":
            sql = _to_pg_sql(sql)
            try:
                cur = self._raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            except psycopg2.InterfaceError:
                # stale pool conn; reconnect this borrow
                self._raw = _POOL.getconn()
                cur = self._raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                cur.execute(sql, tuple(params))
            except psycopg2.errors.DuplicateColumn:
                # additive ALTER TABLE ... ADD COLUMN — match sqlite behaviour where
                # the caller's `except sqlite3.OperationalError: pass` covers this
                self._raw.rollback()
                raise IntegrityError_DupColumn()
            except psycopg2.errors.UniqueViolation:
                self._raw.rollback()
                raise IntegrityError("unique_violation")
            return _Cursor(cur)
        # sqlite
        cur = self._raw.execute(sql, tuple(params))
        return _Cursor(cur)

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

    # Context-manager: sqlite3 commits on success, rolls back on error.
    # For postgres we want the same + return connection to pool.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._kind == "sqlite":
            try:
                if exc_type:
                    self._raw.rollback()
                else:
                    self._raw.commit()
            finally:
                self._raw.close()
            return False
        # postgres
        try:
            if exc_type:
                self._raw.rollback()
            else:
                self._raw.commit()
        finally:
            _POOL.putconn(self._raw)
        return False


class IntegrityError_DupColumn(Exception):
    """Raised by execute() when ALTER TABLE ADD COLUMN hits an existing column.
    The init code catches this in the same place it catches sqlite3.OperationalError."""


def _connect():
    if USE_POSTGRES:
        raw = _POOL.getconn()
        return _Conn(raw, "postgres")
    raw = sqlite3.connect(SQLITE_PATH)
    raw.row_factory = sqlite3.Row
    return _Conn(raw, "sqlite")


# ── Public API used by webapp.py ────────────────────────────────────────
def db():
    """Open a connection. Use as `with db() as c: ...`."""
    return _connect()


def column_names(conn: _Conn, table: str) -> list[str]:
    """Cross-DB equivalent of sqlite's PRAGMA table_info()."""
    if USE_POSTGRES:
        cur = conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = ? AND table_schema = current_schema()",
            (table,),
        )
        return [r["column_name"] for r in cur.fetchall()]
    cur = conn._raw.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def is_duplicate_column_error(exc: BaseException) -> bool:
    return isinstance(exc, (sqlite3.OperationalError, IntegrityError_DupColumn))


def kind() -> str:
    return "postgres" if USE_POSTGRES else "sqlite"
