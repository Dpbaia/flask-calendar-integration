from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, request
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_restful import Api, Resource
from markupsafe import escape
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)

class AwesomeRequestSchema(Schema):
    api_type = fields.String(required=True, description="API type of awesome API")

class AwesomeResponseSchema(Schema):
    message = fields.Str(default='Success')

class AwesomeAPI(MethodResource, Resource):
    @doc(description="First Swagger Get Endpoint Schema", tags=["Swagger"])
    @marshal_with(AwesomeResponseSchema)  # marshalling
    def get(self):
        '''
        Get method represents a GET API method
        '''
        return {'message': 'My First Awesome API'}

class NewClass(MethodResource, Resource):
    @doc(description='My First GET Awesome API.', tags=['Awesome'])
    @use_kwargs(AwesomeRequestSchema, location=('json'))
    @marshal_with(AwesomeResponseSchema)  # marshalling
    def post(self, api_type):
        '''
        Get method represents a GET API method
        '''
        return {'test': 'My First Awesome API'}


api.add_resource(AwesomeAPI, '/awesome')
api.add_resource(NewClass, '/newclass')



app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Awesome Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(AwesomeAPI)
docs.register(NewClass)

@app.route("/")
def hello():
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"

if __name__ == '__main__':
    app.run(debug=True)
