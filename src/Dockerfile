FROM django:python3-onbuild

WORKDIR /usr/src/app

COPY ./gunicornup.sh /
COPY ./pythonstart.sh /
RUN chmod +x /gunicornup.sh && chmod +x /pythonstart.sh && mkdir -p /usr/src/logs/
VOLUME ["/usr/src/logs/","/usr/src/app/monitcollector/static"]
ENTRYPOINT ["/gunicornup.sh"]
