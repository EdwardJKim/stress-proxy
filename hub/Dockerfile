FROM ipython/ipython

USER root
RUN apt-get update && apt-get install -y python3 python3-pip

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY . /srv/hub
WORKDIR /srv/hub

ADD https://raw.githubusercontent.com/minrk/nbbot/master/nbbot.py /srv/hub/nbbot.py
RUN chmod 700 /srv/hub

ENTRYPOINT ["python3", "runner.py"]

