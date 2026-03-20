from pathlib import Path
import sqlite3
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import models.user as user_model


@pytest.fixture()
def db_path(tmp_path):
    return tmp_path / "usersdb.db"


@pytest.fixture()
def use_temp_db(monkeypatch, db_path):
    original_connect = sqlite3.connect

    def _connect(_):
        return original_connect(db_path)

    monkeypatch.setattr(user_model.sqlite3, "connect", _connect)
    user_model.init_db()
    return db_path


def test_init_db_creates_users_table(use_temp_db):
    conn = sqlite3.connect(use_temp_db)
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        ).fetchone()
        assert row is not None
    finally:
        conn.close()


def test_authenticate_user_requires_credentials(use_temp_db):
    assert user_model.authenticate_user("", "x") is None
    assert user_model.authenticate_user("x", "") is None


def test_register_and_authenticate_success(use_temp_db):
    ok, message = user_model.register_user("alice", "pw")
    assert ok is True
    assert "success" in message.lower()

    user = user_model.authenticate_user("alice", "pw")
    assert user == {"id": 1, "name": "alice"}


def test_register_rejects_missing_and_duplicate(use_temp_db):
    ok, message = user_model.register_user("", "pw")
    assert ok is False
    assert "required" in message.lower()

    assert user_model.register_user("bob", "pw")[0] is True
    ok2, message2 = user_model.register_user("bob", "pw")
    assert ok2 is False
    assert "exists" in message2.lower()


def test_user_exists_and_lookup_helpers(use_temp_db):
    assert user_model.user_exists("charlie") is False
    assert user_model.register_user("charlie", "pw")[0] is True
    assert user_model.user_exists("charlie") is True

    by_username = user_model.get_user_by_username("charlie")
    assert by_username["name"] == "charlie"

    by_id = user_model.get_user_by_id(by_username["id"])
    assert by_id["name"] == "charlie"


def test_authenticate_returns_none_for_wrong_password(use_temp_db):
    assert user_model.register_user("dana", "pw")[0] is True
    assert user_model.authenticate_user("dana", "bad") is None


def test_register_user_handles_database_error(monkeypatch):
    monkeypatch.setattr(user_model, "user_exists", lambda username: False)

    class _BadConn:
        def execute(self, *_args, **_kwargs):
            raise sqlite3.Error("boom")

        def commit(self):
            return None

        def close(self):
            return None

    monkeypatch.setattr(user_model, "get_db_connection", lambda: _BadConn())

    ok, message = user_model.register_user("eve", "pw")
    assert ok is False
    assert "database error" in message.lower()
