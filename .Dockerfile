# pull official base image
FROM python:3.11-alpine

# set work directory
WORKDIR /usr/src/cybcrm

# # set environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/cybcrm 

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]