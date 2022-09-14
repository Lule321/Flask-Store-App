FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


RUN mkdir -p /opt/src/deleteStore
WORKDIR /opt/src/deleteStore

COPY store/models.py ./models.py
COPY requirements.txt ./requirements.txt

COPY store/delete.py ./delete.py
COPY store/configuration.py ./configuration.py
RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/deleteStore"


ENTRYPOINT ["python", "./delete.py"]