from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource

from ..schemas.request_schema import RequestSchema
from ..schemas.response_schema import ResponseSchema


class ExampleAPI(MethodResource, Resource):
    # This just determined to what endpoint it will go
    @doc(description="First Swagger Get Endpoint Schema", tags=["Swagger"])
    @marshal_with(ResponseSchema)  # marshalling
    def get(self):
        """
        Get method represents a GET API method
        """
        return {"message": "My First Awesome API"}

    @doc(description="Another POST API.", tags=["test"])
    @use_kwargs(RequestSchema, location=("json"))
    @marshal_with(ResponseSchema)  # marshalling
    def post(self, api_type):
        """
        Get method represents a GET API method
        """
        return {"test": "My First Awesome API"}


class NewClass(MethodResource, Resource):
    @doc(description="My First POST API.", tags=["Awesome"])
    @use_kwargs(RequestSchema, location=("json"))
    @marshal_with(ResponseSchema)  # marshalling
    def post(self, api_type):
        """
        Get method represents a GET API method
        """
        return {"test": "My First Awesome API"}
