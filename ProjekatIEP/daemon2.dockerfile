FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir -p /opt/src/daemon
WORKDIR /opt/src/daemon

COPY store/models.py ./models.py
COPY requirements.txt ./requirements.txt

COPY store/applicationDaemon2.py ./application.py
COPY store/daemon/configuration.py ./configuration.py
RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/daemon"


ENTRYPOINT ["python", "./application.py"]