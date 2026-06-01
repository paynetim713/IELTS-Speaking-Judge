"""sqlite ↔ postgres shim.

Without DATABASE_URL → local sqlite at sessions.db.
With DATABASE_URL set to postgres:// → Supabase / Render Postgres.

Same surface as raw sqlite3: `with db() as c: c.execute('... ?', (...))`.
The one cross-DB awkwardness is column introspection — see column_names().
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
    if _RAW_URL.startswith("postgres://"):
        _RAW_URL = "postgresql://" + _RAW_URL[len("postgres://"):]
    import psycopg2
    import psycopg2.extras
    from psycopg2 import pool as _pg_pool

    _POOL = _pg_pool.ThreadedConnectionPool(1, 6, dsn=_RAW_URL)


if USE_POSTGRES:
    class IntegrityError(Exception):
        pass
else:
    IntegrityError = sqlite3.IntegrityError  # type: ignore[misc]


class IntegrityError_DupColumn(Exception):
    """Raised when ALTER TABLE ADD COLUMN hits an existing column. The init
    code catches it the same way it catches sqlite's OperationalError."""


def _to_pg_sql(sql: str) -> str:
    sql = sql.replace("?", "%s")
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    # postgres REAL is 4-byte single precision; time.time() loses seconds at that range.
    sql = re.sub(r"\bREAL\b", "DOUBLE PRECISION", sql)
    return sql


class _Cursor:
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
    def __init__(self, raw, kind):
        self._raw = raw
        self._kind = kind

    def execute(self, sql, params=()):
        if self._kind == "postgres":
            sql = _to_pg_sql(sql)
            try:
                cur = self._raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            except psycopg2.InterfaceError:
                # Stale pool connection — re-borrow and retry.
                self._raw = _POOL.getconn()
                cur = self._raw.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            try:
                cur.execute(sql, tuple(params))
            except psycopg2.errors.DuplicateColumn:
                self._raw.rollback()
                raise IntegrityError_DupColumn()
            except psycopg2.errors.UniqueViolation:
                self._raw.rollback()
                raise IntegrityError("unique_violation")
            return _Cursor(cur)
        return _Cursor(self._raw.execute(sql, tuple(params)))

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

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
        try:
            if exc_type:
                self._raw.rollback()
            else:
                self._raw.commit()
        finally:
            _POOL.putconn(self._raw)
        return False


def _connect():
    if USE_POSTGRES:
        return _Conn(_POOL.getconn(), "postgres")
    raw = sqlite3.connect(SQLITE_PATH)
    raw.row_factory = sqlite3.Row
    return _Conn(raw, "sqlite")


def db():
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
