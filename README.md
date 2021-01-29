# cltl-template

This repo is a template for the other services.
Each service has its own repo and a Dockerfile.
Their structure will inherit from this repo.

## For a typical Python component

### API
Create an API with domain data classes and an interface providing the functionality of the component.

Use *dataclasses* for the domain objects and avoid custom methods. This makes it possible to deserialize
to `SimpleNamespace` objects. Otherwise you eventually need to use a custom deserializer to convert from
JSON inputs to Python class instances. 

Export it as Python library using setuptools to the cltl-requirements repository.

### REST endpoint
Provide a REST endpoint with an OpenAPI spec generated from the data classes.
The template uses Flask with Marshmallow for this.

### Event handler
Provide an Event handler using the data classes, exposing an AsyncAPI sped.

### Command line
Create an main class that let's you invoke your service as Pyhton script from the command line.

### Python library

Create a library package with your impementation and install it to cltl-requirements.
The library package may contain the API package. 

### Docker image

Create a Docker image that runs your compoenent, including the required REST endpoints/Event handlers.

