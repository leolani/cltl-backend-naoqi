from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.yaml_utils import load_yaml_from_docstring
from marshmallow_dataclass import class_schema

from cltl.demo.api import ExampleOutput, ExampleInput
from cltl.demo.implementation import DummyExampleComponent


class OpenAPISpec:
    def __init__(self, *args, **kwargs):
        self.spec = APISpec(*args, **kwargs)

    @property
    def to_yaml(self):
        return self.spec.to_yaml()

    @property
    def to_dict(self):
        return self.spec.to_dict()

    @property
    def components(self):
        return self.spec.components

    def path(self, path):
        def wrapped(func):
            self.spec.path(path,
                           description=func.__doc__.partition('\n')[0],
                           operations=load_yaml_from_docstring(func.__doc__))
            return func
        return wrapped


api = OpenAPISpec(title="Template",
                  version="0.0.1",
                  openapi_version="3.0.2",
                  info=dict(description="Leolani component template"),
                  plugins=[MarshmallowPlugin()], )


api.components.schema("ExampleInput", schema=class_schema(ExampleInput))
api.components.schema("ExampleOutput", schema=class_schema(ExampleOutput))


@api.path("/template/api/foo/bar")
def foo_bar(input):
    """Short Description included in OpenAPI spec

    A longer description can go here.

    The yaml snippet below is included in the OpenAPI spec for the endpoint:
    ---
    get:
      operationId: rest.endpoint.foo_bar
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExampleOutput'
          description: Get foo bars
      parameters:
      - in: query
        name: times
        schema:
          $ref: '#/components/schemas/ExampleInput'
    """
    return DummyExampleComponent().foo_bar(input)


if __name__ == '__main__':
    with open("template_spec.yaml", "w") as f:
        f.write(api.to_yaml())
