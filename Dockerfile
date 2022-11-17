FROM python:3.8-alpine

RUN apk update
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt --src /usr/local/src

COPY . .
ENV FLASK_APP=./restapi/main.py

RUN chmod +x bootstrap.sh
CMD ["/app/bootstrap.sh"]
