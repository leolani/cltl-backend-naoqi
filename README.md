# cltl-backend-naoqi

NaoQI Backend for the Pepper Robot.

## Functionality

This repository provides a Docker container that runs an web server that supports connections of the client sources
provided in the `cltl.backend.source.client_source` module of the
[Leolani Backend](https://github.com/leolani/cltl-backend/).

The docker image provides endpoints for Audio, Images and connects to the robot through TCP to retrieve and send
signals.

#### Audio

The container exposes an endpoint at `/audio` (GET) that provides an audio stream. The format of the stream is indicated
by the mine type indicated in the response. Currently, this will be chunked audio data with mime type `audio/L16`, i.e.
raw 16bit audio. In the mime type header, additional parameters for `rate`, `channels` and `frame_size` are provided.

#### Images

The container exposes an endpoint at `/image` (GET) that provides an image captured at invocation time. The endpoint
returns a JSON object corresponding to
[cltl.backend.api.camera.Image](https://github.com/leolani/cltl-backend/blob/eliza/src/cltl/backend/api/camera.py)
that contains the raw image data, the image dimensions and depth information. Image dimensions are also inlcude in the
mime type header of the response.

## Build the backend Docker container

To build the docker image run

    make build

This will create a docker image with tag `cltl-backend-naoqi`. To verify the build was successful run

    make test

## Run the backend Docker container

To run the docker image use:

    docker run --rm -it -e CLTL_NAOQI_IP="192.0.0.1" -p 8000:8000 cltl-backend-naoqi

It is mandatory to provide the IP of the Pepper robot in the `CLTL_NAOQI_IP` environment variable. Further
configurations can be set through environment variables, for a list run

    docker run --rm -it cltl-backend-naoqi python app.py --help

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/leolani/cltl-combot/blob/main/LICENCE) for more
information.

## Authors

* [Taewoon Kim](https://tae898.github.io/)
* [Thomas Baier](https://www.linkedin.com/in/thomas-baier-05519030/)
* [Selene Báez Santamaría](https://selbaez.github.io/)
* [Piek Vossen](https://github.com/piekvossen)