FROM python:3.9-slim as base

WORKDIR /usr/src/app

RUN apt update && \
    apt install -qqy \
    libgnutls28-dev \
    libcurl4-gnutls-dev \
    libexpat1-dev \
    gettext \
    libz-dev \
    libssl-dev \
    gcc && \
    apt install libcurl4-openssl-dev -qqy && \
    apt --purge autoremove -y && \
    apt clean

FROM base as python-requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python-requirements
COPY gunicorn.conf.py ./
COPY run.py ./
COPY ./app ./app

ENTRYPOINT ["gunicorn"]
CMD ["run:app", "--reload"]