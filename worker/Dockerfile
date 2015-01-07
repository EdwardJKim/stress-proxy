FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY . /srv/worker
WORKDIR /srv/worker
ENTRYPOINT ["python3", "workers.py"]

