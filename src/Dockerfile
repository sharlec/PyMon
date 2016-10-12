FROM python:3.5-alpine

RUN apk add --update --no-cache postgresql-client postgresql-dev sqlite g++
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

COPY ./gunicornup.sh /
COPY ./pythonstart.sh /
RUN chmod +x /gunicornup.sh && chmod +x /pythonstart.sh && mkdir -p /usr/src/logs/
VOLUME ["/usr/src/logs/","/usr/src/app/static"]
ENTRYPOINT ["/gunicornup.sh"]
