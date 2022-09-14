FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir -p /opt/src/deleteAuth
WORKDIR /opt/src/deleteAuth

COPY authentication/models.py ./models.py
COPY requirements.txt ./requirements.txt

COPY authentication/delete.py ./delete.py
COPY authentication/configuration.py ./configuration.py
RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/deleteAuth"


ENTRYPOINT ["python", "./delete.py"]