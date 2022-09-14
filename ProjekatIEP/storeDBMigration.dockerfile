FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir -p /opt/src/store
WORKDIR /opt/src/store

COPY store/migrate.py ./migrate.py
COPY store/configuration.py ./configuration.py
COPY store/models.py ./models.py
COPY requirements.txt ./requirements.txt


ENV PYTHONPATH="/opt/src/store"
RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]