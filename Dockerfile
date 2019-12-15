FROM ubuntu:18.04

ADD . /code
WORKDIR /code
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt

CMD celery worker -A dobetter --loglevel=info --concurrency=1