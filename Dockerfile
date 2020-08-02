FROM python:3.6.5

RUN apt-get update
RUN apt-get install -y git python3-pip libopus0 libav-tools

WORKDIR /usr/src/patreon

ADD . /usr/src/patreon

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt



ENTRYPOINT ["python3", "patreon.py"]