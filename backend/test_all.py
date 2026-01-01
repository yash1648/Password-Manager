import json
import uuid
import importlib
import pytest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace


from crypto_utils import (
    generate_secure_token,
    constant_time_compare,
    generate_session_id,
    validate_password_strength,
    sanitize_input,
)
from auth import (
    generate_salt,
    hash_master_password,
    verify_master_password,
    generate_jwt_token,
    decode_jwt_token,
)
import database.db_factory as db_factory
from database.postgres_repository import PostgresRepository
from database.mongodb_repository import MongoRepository


class FakeRepo:
    def __init__(self):
        self.users_by_username = {}
        self.users_by_email = {}
        self.passwords = {}

    def initialize(self):
        return None

    def close(self):
        return None

    def create_user(self, username: str, email: str, password_hash: str, salt: str):
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "master_password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.users_by_username[username] = user
        self.users_by_email[email] = user
        self.passwords[user_id] = []
        return user

    def get_user_by_username(self, username: str):
        return self.users_by_username.get(username)

    def get_user_by_email(self, email: str):
        return self.users_by_email.get(email)

    def get_user_by_id(self, user_id: str):
        for user in self.users_by_username.values():
            if user["id"] == user_id:
                return user
        return None

    def create_password(
        self,
        user_id: str,
        website_url: str,
        website_name: str,
        username: str,
        encrypted_password: str,
        iv: str,
        notes: str = "",
    ):
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "user_id": user_id,
            "website_url": website_url,
            "website_name": website_name,
            "username": username,
            "encrypted_password": encrypted_password,
            "iv": iv,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
        }
        self.passwords[user_id].append(entry)
        return entry

    def get_passwords(self, user_id: str):
        return list(self.passwords.get(user_id, []))

    def get_password_by_id(self, password_id: str, user_id: str):
        for p in self.passwords.get(user_id, []):
            if p["id"] == password_id:
                p["last_used"] = datetime.now(timezone.utc).isoformat()
                return p
        return None

    def update_password(self, password_id: str, user_id: str, data):
        for p in self.passwords.get(user_id, []):
            if p["id"] == password_id:
                for k, v in data.items():
                    p[k] = v
                p["updated_at"] = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def delete_password(self, password_id: str, user_id: str):
        items = self.passwords.get(user_id, [])
        for i, p in enumerate(items):
            if p["id"] == password_id:
                del items[i]
                return True
        return False

    def search_passwords(self, user_id: str, query: str):
        return [p for p in self.passwords.get(user_id, []) if query.lower() in p["website_url"].lower()]

    def get_password_count(self, user_id: str):
        return len(self.passwords.get(user_id, []))


@pytest.fixture
def fake_repo():
    return FakeRepo()


def test_crypto_utils_basic():
    t1 = generate_secure_token(16)
    t2 = generate_secure_token(16)
    assert isinstance(t1, str)
    assert t1 != t2
    assert constant_time_compare("a", "a") is True
    assert constant_time_compare("a", "b") is False
    sid = generate_session_id()
    assert isinstance(sid, str) and len(sid) > 0
    ok, msg = validate_password_strength("Abcdef12!")
    assert ok is True
    assert "Password is strong" in msg
    ok2, msg2 = validate_password_strength("short")
    assert ok2 is False
    assert "at least 8" in msg2
    s = sanitize_input("\x00 test ")
    assert s == "test"


def test_auth_hash_and_verify():
    salt = generate_salt()
    hp = hash_master_password("StrongPass123!", salt)
    assert isinstance(hp, str) and len(hp) > 10
    assert verify_master_password("StrongPass123!", salt, hp) is True
    assert verify_master_password("WrongPass", salt, hp) is False


def test_auth_jwt_roundtrip():
    secret = "unit-secret"
    token = generate_jwt_token("u1", "user1", secret, "HS256", 1)
    payload = decode_jwt_token(token, secret, "HS256")
    assert payload is not None
    assert payload["user_id"] == "u1"
    assert payload["username"] == "user1"


def test_db_factory_selection(monkeypatch):
    monkeypatch.setattr(PostgresRepository, "initialize", lambda self: None)
    monkeypatch.setattr(MongoRepository, "initialize", lambda self: None)
    cfg_pg = SimpleNamespace(DATABASE_TYPE="postgresql", POSTGRES_URI="postgresql://localhost/db", MONGODB_URI="")
    cfg_mg = SimpleNamespace(DATABASE_TYPE="mongodb", POSTGRES_URI="", MONGODB_URI="mongodb://localhost/db")
    repo_pg = db_factory.get_repository(cfg_pg)
    repo_mg = db_factory.get_repository(cfg_mg)
    assert isinstance(repo_pg, PostgresRepository)
    assert isinstance(repo_mg, MongoRepository)
    with pytest.raises(ValueError):
        db_factory.get_repository(SimpleNamespace(DATABASE_TYPE="sqlite"))


def test_app_routes_with_fake_repo(monkeypatch, fake_repo):
    monkeypatch.setattr(db_factory, "get_repository", lambda cfg: fake_repo)
    app_module = importlib.import_module("app")
    app_module.db_repo = fake_repo
    client = app_module.app.test_client()

    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert "status" in data and data["status"] == "healthy"

    payload = {"username": "alice", "email": "alice@example.com", "master_password": "StrongPass123!"}
    rr = client.post("/api/auth/register", data=json.dumps(payload), content_type="application/json")
    assert rr.status_code == 201
    reg = rr.get_json()
    assert "token" in reg and "user" in reg
    token = reg["token"]

    rl = client.post(
        "/api/auth/login",
        data=json.dumps({"username": "alice", "master_password": "StrongPass123!"}),
        content_type="application/json",
    )
    assert rl.status_code == 200
    login = rl.get_json()
    assert "token" in login

    h = {"Authorization": f"Bearer {token}"}
    gp = client.get("/api/passwords", headers=h)
    assert gp.status_code == 200
    assert gp.get_json()["passwords"] == []

    cp = client.post(
        "/api/passwords",
        data=json.dumps(
            {
                "website_url": "https://example.com",
                "website_name": "Example",
                "username": "alice_u",
                "encrypted_password": "enc",
                "iv": "iv",
                "notes": "n",
            }
        ),
        content_type="application/json",
        headers=h,
    )
    assert cp.status_code == 201
    created = cp.get_json()["password"]
    pid = created["id"]

    gp2 = client.get(f"/api/passwords/{pid}", headers=h)
    assert gp2.status_code == 200
    assert gp2.get_json()["password"]["id"] == pid

    up = client.put(
        f"/api/passwords/{pid}",
        data=json.dumps({"username": "alice_updated"}),
        content_type="application/json",
        headers=h,
    )
    assert up.status_code == 200

    sp = client.post(
        "/api/passwords/search",
        data=json.dumps({"url": "example"}),
        content_type="application/json",
        headers=h,
    )
    assert sp.status_code == 200
    assert len(sp.get_json()["passwords"]) == 1

    dp = client.delete(f"/api/passwords/{pid}", headers=h)
    assert dp.status_code == 200


def test_app_password_limit(monkeypatch, fake_repo):
    monkeypatch.setattr(db_factory, "get_repository", lambda cfg: fake_repo)
    app_module = importlib.import_module("app")
    app_module.db_repo = fake_repo
    app_module.app.config["MAX_PASSWORD_ENTRIES"] = 1
    client = app_module.app.test_client()

    rr = client.post(
        "/api/auth/register",
        data=json.dumps({"username": "bob", "email": "bob@example.com", "master_password": "Abcd1234!"}),
        content_type="application/json",
    )
    token = rr.get_json()["token"]
    h = {"Authorization": f"Bearer {token}"}

    cp1 = client.post(
        "/api/passwords",
        data=json.dumps(
            {
                "website_url": "https://site1.com",
                "website_name": "Site1",
                "username": "u1",
                "encrypted_password": "enc",
                "iv": "iv",
                "notes": "",
            }
        ),
        content_type="application/json",
        headers=h,
    )
    assert cp1.status_code == 201

    cp2 = client.post(
        "/api/passwords",
        data=json.dumps(
            {
                "website_url": "https://site2.com",
                "website_name": "Site2",
                "username": "u2",
                "encrypted_password": "enc",
                "iv": "iv",
                "notes": "",
            }
        ),
        content_type="application/json",
        headers=h,
    )
    assert cp2.status_code == 400
