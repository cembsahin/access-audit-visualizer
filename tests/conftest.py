import io
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as app_module  # noqa: E402
from models import db, AccessRecord  # noqa: E402


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app_module.app.config["WTF_CSRF_ENABLED"] = False

    with app_module.app.app_context():
        db.drop_all()
        db.create_all()

    with app_module.app.test_client() as client:
        yield client

    with app_module.app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_csv_bytes():
    csv_content = (
        "username,department,role,status,last_login\n"
        "jsmith,Engineering,Software Engineer,Active,2026-08-01\n"
        "kpatel,IT,System Administrator,Active,2025-12-15\n"
        "tclark,IT,Domain Admin,Suspended,2025-09-10\n"
        "nnguyen,Engineering,DevOps Admin,Active,2025-08-12\n"
    )
    return io.BytesIO(csv_content.encode("utf-8"))
