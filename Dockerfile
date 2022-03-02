FROM ubuntu:20.04
LABEL org.opencontainers.image.authors="subhajti.mandal@nagarro.com"
RUN apt-get update -y && apt-get install -y python3-pip python-dev
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 8000
ENTRYPOINT [ "python3" ]
CMD [ "setup.py" ]