FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

COPY store/models.py ./models.py
COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

RUN mkdir -p ./warehouse
WORKDIR ./warehouse

COPY store/warehouse/application.py ./application.py
COPY store/warehouse/configuration.py ./configuration.py

ENV PYTHONPATH="/opt/src/store"


ENTRYPOINT ["python", "./application.py"]