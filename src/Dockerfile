FROM django:python3-onbuild

WORKDIR /usr/src/app

COPY ./gunicornup.sh /
RUN chmod +x /gunicornup.sh && mkdir -p /usr/src/logs/
VOLUME ["/usr/src/logs/"]
ENTRYPOINT ["/gunicornup.sh"]
