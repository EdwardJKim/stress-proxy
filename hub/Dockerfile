FROM jupyter/notebook

USER root
RUN apt-get update && apt-get install -y python3 python3-pip curl libcurl3-openssl-dev

ENV PYCURL_SSL_LIBRARY openssl

RUN pip3 install pycurl

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY . /srv/hub
WORKDIR /srv/hub

RUN chmod 700 /srv/hub

ENTRYPOINT ["python3", "runner.py"]

