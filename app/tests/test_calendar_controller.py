import mock

from app.api.controllers.google_calendar import GoogleCalendarsController

controller = GoogleCalendarsController()


class DictBuilder:
    def __init__(self) -> None:
        self._sa_instance_state = 1
        self.id = 1
        self.token = 1
        self.refresh_token = 1
        self.token_uri = 1
        self.client_id = 1
        self.client_secret = 1
        self.scopes = 1
        self.expiry = 1
        self.user_type = 1


class FilterMock(mock.Mock):
    def first(*args, **kwargs):
        return DictBuilder()


class QueryMock(mock.Mock):
    def filter(*args, **kwargs):
        return FilterMock


class OauthStorageMock(mock.Mock):
    query = QueryMock


@mock.patch(
    "app.api.controllers.google_calendar.OauthStorage", new_callable=OauthStorageMock
)
@mock.patch("app.api.controllers.google_calendar.build")
@mock.patch.dict(
    "app.api.controllers.google_calendar.OauthStorage.__dict__", {"test": "test"}
)
def test_get_single_day(mock_google_api, mock_oauthstorage):
    result = controller.get_single_day_calendar("21-11-2022")
    mock_google_api.assert_called_once()
    assert result["weekday"] == "Segunda"


@mock.patch(
    "app.api.controllers.google_calendar.OauthStorage", new_callable=OauthStorageMock
)
@mock.patch("app.api.controllers.google_calendar.build")
@mock.patch.dict(
    "app.api.controllers.google_calendar.OauthStorage.__dict__", {"test": "test"}
)
def test_get_30_days(mock_google_api, mock_oauthstorage):
    controller.get_thirty_days_calendar()
    mock_google_api.assert_called_once()


@mock.patch("app.api.controllers.google_calendar.build")
def test_create_event(mock_google_api):
    result = controller.create_event(
        "test", "21-11-2022", "12:00", "1:00", "test@gmail.com"
    )
    mock_google_api.assert_called_once()
    assert result == "Segunda"
