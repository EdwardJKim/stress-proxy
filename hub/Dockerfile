FROM ipython/ipython

USER root
RUN apt-get update && apt-get install -y python3 python3-pip

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY . /srv/hub
WORKDIR /srv/hub

USER nobody
ENTRYPOINT ["python3", "hub.py"]

