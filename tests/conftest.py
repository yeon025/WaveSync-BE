import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.database.deps import get_db


@pytest.fixture(scope="session")
def app():
    return fastapi_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_image_bytes():
    # create a simple 10x10 red PNG image
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


class DummyDB:
    def __init__(self, resonator_names=None, weapon_names=None, raise_on_execute=None):
        self._resonator_names = resonator_names or ["ResonatorX"]
        self._weapon_names = weapon_names or ["WeaponY"]
        self._raise = raise_on_execute

    def execute(self, stmt):
        if self._raise:
            raise self._raise
        # crude detection by string representation
        s = str(stmt)
        if "ResonatorMaster" in s:
            return DummyResult([(name,) for name in self._resonator_names])
        if "WeaponMaster" in s:
            return DummyResult([(name,) for name in self._weapon_names])
        return DummyResult([])

    def close(self):
        pass


class DummyResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


@pytest.fixture
def dummy_db():
    return DummyDB()


@pytest.fixture
def override_db(app, dummy_db):
    # override the get_db dependency for tests
    def _get_db_override():
        try:
            yield dummy_db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.pop(get_db, None)
