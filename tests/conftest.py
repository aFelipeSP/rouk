
import pytest
from rouk import create_app
from rouk.db import get_db

@pytest.fixture
def app():
    app = create_app()

    yield app
