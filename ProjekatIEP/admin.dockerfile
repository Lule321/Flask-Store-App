FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /opt/src/admin
WORKDIR /opt/src/admin



COPY store/models.py ./models.py
COPY requirements.txt ./requirements.txt

COPY store/applicationAdmin.py ./application.py
COPY store/admin/configuration.py ./configuration.py
RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/admin"


ENTRYPOINT ["python", "./application.py"]