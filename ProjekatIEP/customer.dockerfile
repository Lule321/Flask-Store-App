FROM python:3

ENV TZ=Europe/Belgrade
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /opt/src/customer
WORKDIR /opt/src/customer

COPY store/models.py ./models.py
COPY requirements.txt ./requirements.txt

COPY store/applicationCustomer.py ./application.py
COPY store/customer/configuration.py ./configuration.py
RUN pip install -r ./requirements.txt
ENV PYTHONPATH="/opt/src/customer"


ENTRYPOINT ["python", "./application.py"]