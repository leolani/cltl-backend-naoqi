# cltl-backend-naoqi

NaoQI Backend for the Pepper Robot.

## Backend server

This repository provides a web server that supports connections of the client sources provided in the
`cltl.backend.source.client_source` module of the [Leolani Backend](https://github.com/leolani/cltl-backend/)
to the Pepper robot. The web server provides endpoints for Audio, Images as well as Text to Speech.

The web server can be run on the Pepper robot directly, or from a docker image that can be built from this repository.
Mind that the Docker image will only run on Linux due to networking issues (see below).

#### Audio

The container exposes an endpoint at `/audio` (GET) that provides an audio stream. The format of the stream is indicated
by the mine type indicated in the response. Currently, this will be chunked audio data with mime type `audio/L16`, i.e.
raw 16bit audio. In the mime type header, additional parameters for `rate`, `channels` and `frame_size` are provided.

#### Images

The container exposes an endpoint at `/video` (GET) that provides an image captured at invocation time. The endpoint
returns a JSON object corresponding to
[cltl.backend.api.camera.Image](https://github.com/leolani/cltl-backend/blob/eliza/src/cltl/backend/api/camera.py)
that contains the raw image data, the image dimensions and depth information. Image dimensions are also inlcude in the
mime type header of the response.

## Run the backend on the robot

To run the backend directly on the robot, the `cltl.backend-naoqi` package with its dependencies needs to be installed
and run on the robot.

### Package installation

On pepper, a rather old Python version is installed, which causes issues with `pip`. Also, root access of
the [`nao` user](http://doc.aldebaran.com/2-4/dev/tools/opennao.html#naoqi-os-user-accounts)
is restricted. `pip` can still be upgraded for the _nao_ user using (run in a separate directory)

```bash
wget https://files.pythonhosted.org/packages/ca/1e/d91d7aae44d00cd5001957a1473e4e4b7d1d0f072d1af7c34b5899c9ccdf/pip-20.3.3.tar.gz
pip install --user pip-20.3.3.tar.gz
```

Since we do not want to interfere with the Python environment on pepper, we install the package in a virutal
environment. **For the installation the `scripts/download_libs.sh` and
`scripts/install_libs.sh` scripts are provided.** First execute the download script on your local machine (it fails on
the robot due to ssl issues). This will downlaod all necessary packages to a folder called `lib/`. Then copy this folder
to the robot using scp:

        scp -r lib nao@<robot-ip>:<cltl-backend-install-dir>
        scp -r scripts nao@<robot-ip>:<cltl-backend-install-dir>

Then log in to the robot, navigate into the directory where the `lib/` folder was uploaded, and run the
`scripts/install_libs.sh` script. This will create a virtual environment and install the packages in `lib/`.

### Running the backend

To run the backend we need to find an unused port that can be used by the web server
<del>and make sure
the [firewall on Pepper allows access it](http://doc.aldebaran.com/2-4/dev/tools/opennao.html#firewall-network-access-limitation)
.</del> By default the server uses port `8000`, which typically is available.

To run the server, execute the `scripts/backend_naoqi.sh` script with one of the options `start`, `run`, `state`,
or `stop`. The `start` option can be used to run the server in the background using `nohup`, i.e. you can disconnect
from the robot after starting the server. The `run` option will start the script directly and is equivalent to

```
source venv/bin/activate
python -m cltl.naoqi --naoqi-ip 127.0.0.1 --port 8000
```

### Configuration

Additional configuration parameters can be added when starting the web server, for a comprehensive list run

    python -m cltl.naoqi --help

This configuration options can be either specified as command line options or environment variables.

#### Text to speech

The robot has Text to Speech (TTS) as built-in feature. To use TTS on the robot, send a `POST` requests to the
`text/` (POST) endpoint with the text as payload and mime type `text/plain`. The text posted to the robot can
be [annotated with animation instructions](http://doc.aldebaran.com/2-1/naoqi/audio/alanimatedspeech.html).

## Backend Docker container

**At the current moment running the Docker container on works on LINUX, as the `--network host`
option for Docker is only available on LINUX and some services registered with the qi framework are not visible to the
ALAudioDevice Module when we run inside the Docker container with a bridge network.**

### Build the backend Docker container

To build the docker image run

    make docker

This will create a docker image with tag `cltl-backend-naoqi`. To verify the build was successful run

    make test

### Run the backend Docker container

To run the docker image use:

    docker run --rm -it -e CLTL_NAOQI_IP="192.0.0.1" --network host cltl/cltl-backend-naoqi

It is mandatory to provide the IP of the Pepper robot in the `CLTL_NAOQI_IP` environment variable. Further
configurations can be set through environment variables, for a list run

    docker run --rm -it cltl/cltl-backend-naoqi python -m cltl.naoqi --help

## Test if the backend is working

To test if the backend is working we can curl the REST API of the backend. The following tests require
`numpy` and `cv2` to be installed for python and the `jq` and `sox` command line applications to be installed.
Alternatively redirect the output of the `curl` command to a file and check the content manually.

**When testing /video, hit `Enter` on the image to close it. When testing /audio, mind the echo..**

```shell
curl <backend_ip:port>/video | jq -c '.image' | python -c 'import cv2; import numpy; import json; cv2.imshow("img", numpy.array(json.loads(input()), dtype=np.uint8)); cv2.waitKey(0); cv2.destroyAllWindows()'
curl -N <backend_ip:port>/audio |  play -t raw -e signed -b 16 -c 1 -r 16000 -
curl -H "Content-Type: text/plain" --data "Hallo Stranger!" <backend_ip:port>/text
```

## Unit test

The unit tests in this repository require the NAOqi SDK and Python 2.7 to be installed. They are, however, included in
the Docker image provided by this repository and can be run with:

    make test

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