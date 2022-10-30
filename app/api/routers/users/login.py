from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource

from ...schemas.request_schema import RequestSchema
from ...schemas.response_schema import ResponseSchema

# # create login endpoint
# class ExampleAPI(MethodResource, Resource):
#     @doc(description="Another POST API.", tags=["test"])
#     @use_kwargs(RequestSchema, location=("json"))
#     @marshal_with(ResponseSchema)  # marshalling
#     def post(self, api_type):
#         """
#         Get method represents a GET API method
#         """
#         return {"test": "My First Awesome API"}
