from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from .... import app

app.config.update(
    {
        "APISPEC_SPEC": APISpec(
            title="Calendar Project",
            version="v1",
            plugins=[MarshmallowPlugin()],
            openapi_version="2.0.0",
        ),
        "APISPEC_SWAGGER_URL": "/swagger/",  # URI to access API Doc JSON
        "APISPEC_SWAGGER_UI_URL": "/swagger-ui/",  # URI to access UI of API Doc
    }
)
