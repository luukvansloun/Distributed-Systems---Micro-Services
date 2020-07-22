# base image
FROM python:3.8.0-alpine

# install dependencies
RUN apk update && \
	apk add --virtual build-deps gcc python-dev musl-dev && \
	apk add postgresql-dev && \
	apk add netcat-openbsd

# set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip3 install -r requirements.txt

# add app
COPY . /usr/src/app

# run server
CMD python3 client.py run -H 0.0.0.0