FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication/migrate.py ./migrate.py
COPY authentication/configuration.py ./configuration.py
COPY authentication/models.py ./models.py
COPY requirements.txt ./requirements.txt


ENV PYTHONPATH="/opt/src/authentication"
RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]