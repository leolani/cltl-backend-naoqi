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

#### Text to speech

The robot has Text to Speech (TTS) as built-in feature. To use TTS on the robot send a `POST` requests to the 
`text/` (POST) endpoint with the text as payload with mime type `text/plain`.

## Build the backend Docker container

To build the docker image run

    make docker

This will create a docker image with tag `cltl-backend-naoqi`. To verify the build was successful run

    make test

## Run the backend on the robot

To run the backend directly on the robot the `cltl.backend-naoqi` package with its dependencies needs to be installed
on the robot, make sure the ports of the web server are  open and ensure the backend is started when the robot starts.

### Package installation

On pepper a rather old Python version is installed, which causes issues with `pip`. Also,
root access of the [`nao` user](http://doc.aldebaran.com/2-4/dev/tools/opennao.html#naoqi-os-user-accounts)
is restricted. `pip` can still be upgraded for the user using (run in a separate directory)

```bash
wget https://files.pythonhosted.org/packages/ca/1e/d91d7aae44d00cd5001957a1473e4e4b7d1d0f072d1af7c34b5899c9ccdf/pip-20.3.3.tar.gz
pip install --user pip-20.3.3.tar.gz
```

Since we do not want to interfere with the Python environment on pepper we
install the package in a virutal environment. **For the installation the `scripts/install_libs.sh`
is provided.** Copy it to the robot and execute it. This will create a virtual environment,
download the necessary packages and install them.

**TODO** Downloads in the installation script are changed now to `http`, if the installation script still fails due to ssl issues, download the packages on your local machine
and upload them to the robot via `scp`. Then remove the download code from the installation script and run it.

### Running the backend

To run the backend we need to find an unused port that can be used by the web server
<del>and make sure the [firewall on Pepper allows access it](http://doc.aldebaran.com/2-4/dev/tools/opennao.html#firewall-network-access-limitation).

Once the package is installed it can be run with (`--port` is optional if port 8000 is available on the robot)

```
source venv/bin/activate
python -m cltl.naoqi --naoqi-ip 127.0.0.1 --port 8000
```
**This is also provided in the `scripts/run_backend_naoqi.sh` script.**

### Run at startup (**WIP**)

NaoQi startup is described [here](http://doc.aldebaran.com/2-4/dev/tools/naoqi.html#naoqi-automatic-startup).
We need to figure out a way run the backend at startup.

Try if cron is available on the robot and add an entry there (see [here](https://superuser.com/a/415609)):

    crontab -e
    # Add in the editor:
    @reboot /home/nao/scripts/run_backend_naoqi.sh

Make sure execution is allowed for the script.



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

To test if the backend is working we can curl the REST API of the backend. The following tests require
`numpy` and `cv2` to be installed for python and the `sox` command line application to be installed.

**When testing /video, hit `Enter` on the image to close it. When testing /audio, mind the echo..**
```shell
curl <backend_ip:port>/video | jq -c '.image' | python -c 'import cv2; import numpy; import json; cv2.imshow("img", numpy.array(json.loads(input()), dtype=np.uint8)); cv2.waitKey(0); cv2.destroyAllWindows()'
curl -N <backend_ip:port> |  play -t raw -e signed -b 16 -c 1 -r 16000 -
curl --data "Hallo Stranger!" <backend_ip:port>/text
```

## Unit test

The unit tests in this repository require the NAOqi SDK and Python 2.7 to be installed.
They are, however, included in the Docker image provided by this repository and can be run with:

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