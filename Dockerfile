FROM python:2.7-stretch
MAINTAINER info@vizzuality.com

ENV NAME forest-change-analysis-elastic
ENV USER microservice

RUN apt-get -y update && apt-get -y upgrade && \
   apt-get install -y bash git openssl \
   libffi-dev gcc musl-dev libgeos-3.5.1

RUN addgroup $USER && adduser --shell /bin/bash --disabled-login --ingroup $USER $USER

RUN easy_install pip && pip install --upgrade pip
RUN pip install gunicorn gevent

RUN mkdir -p /opt/$NAME
COPY requirements.txt /opt/$NAME/requirements.txt
RUN cd /opt/$NAME && pip install -r requirements.txt

COPY entrypoint.sh /opt/$NAME/entrypoint.sh
COPY main.py /opt/$NAME/main.py
COPY test.py /opt/$NAME/test.py
COPY gunicorn.py /opt/$NAME/gunicorn.py

# Copy the application folder inside the container
WORKDIR /opt/$NAME
COPY ./gladanalysis /opt/$NAME/gladanalysis
COPY ./microservice /opt/$NAME/microservice

RUN chown -R $USER:$USER /opt/$NAME

# Tell Docker we are going to use this ports
EXPOSE 62000
USER $USER

# Launch script
ENTRYPOINT ["./entrypoint.sh"]
