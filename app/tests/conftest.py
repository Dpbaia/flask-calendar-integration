import pytest

from app.api.config.settings import config
from main import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.from_object(config)
    app.testing = True
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
