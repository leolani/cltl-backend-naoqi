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

## Run the backend on the robot

**WIP**

To run the backend directly on the robot we need to install the `cltl.backend-naoqi`
package with its dependencies on the robot, make sure the ports of the web server are
open and ensure the backend is started when the robot starts.

### Package installation

On pepper a rather old Python version is installed, which causes issues with pip. Also,
root access of the [`nao` user](http://doc.aldebaran.com/2-4/dev/tools/opennao.html#naoqi-os-user-accounts)
is restricted. `pip` can still be upgraded for the user using (run in a separate directory)

```bash
wget https://files.pythonhosted.org/packages/ca/1e/d91d7aae44d00cd5001957a1473e4e4b7d1d0f072d1af7c34b5899c9ccdf/pip-20.3.3.tar.gz
pip install --user pip-20.3.3.tar.gz
```

Since we do not want to interfere with the Python environment on pepper we
install the package in a virutal environment. For the installation the `scripts/install_libs.sh`
is provided. Copy it to the robot and execute it. This will create a virtual environment,
download the necessary packages and install them.

### Running the backend

To run the backend we need to find an unused port that can be used by the web server and
make sure the [firewall on Pepper allows access it](http://doc.aldebaran.com/2-4/dev/tools/opennao.html#firewall-network-access-limitation).

Once the package is installed it can be run with

```
source venv/bin/activate
python -m cltl.naoqi --naoqi-ip 127.0.0.1
```
This is also provided in the `scripts/run_backend_naoqi.sh` script.

### Run at startup

NaoQi startup is described [here](http://doc.aldebaran.com/2-4/dev/tools/naoqi.html#naoqi-automatic-startup).
We need to figure out a way run the backend at startup.


## Run the backend Docker container

**At the current moment the instructions below only work on LINUX, as the `--network host`
option for Docker is only available on LINUX and some services registered with the qi framework
are not visible to the ALAudioDevice Module when we run inside the Docker container with
a bridge network.**

To run the docker image use:

    docker run --rm -it -e CLTL_NAOQI_IP="192.0.0.1" --network host cltl/cltl-backend-naoqi

It is mandatory to provide the IP of the Pepper robot in the `CLTL_NAOQI_IP` environment variable. Further
configurations can be set through environment variables, for a list run

    docker run --rm -it cltl/cltl-backend-naoqi python -m cltl.naoqi --help

## Test if the backend is working

**WIP**

To test if the backend is working we can curl the REST API of the backend

```shell
curl <backend ip>/video
curl <backend ip>/audio
curl --data "Hallo Stranger!" <backend ip>/text
```

## Unit test

The unit tests in this repository require the NAOqi SDK and Python 2.7 to be installed.
They are, however, included in the Docker image provided by this repository and can be run with:

    make build
    docker run --rm -it cltl/cltl-backend-naoqi python -m unittest discover


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