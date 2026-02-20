import pytest
from app import create_app, db as _db
from app.models.user import User
from app.models.project import Project


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(db):
    u = User(email="test@example.com", name="Test User")
    u.set_password("password123")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def auth_headers(client, user):
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    token = resp.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def project(db, user):
    p = Project(name="Test Project", description="A test project", owner_id=user.id)
    db.session.add(p)
    db.session.commit()
    return p
