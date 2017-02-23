#FROM debian:stretch
#FROM ubuntu:16.10
#
#RUN apt-get update && apt-get install -y --no-install-recommends \
#	r-base r-cran-rpostgresql r-cran-jsonlite make g++

FROM alpine:edge

RUN apk add --update --no-cache R R-dev make g++ wget autoconf postgresql-dev \
	&& wget https://cran.r-project.org/src/contrib/RPostgreSQL_0.4-1.tar.gz https://cran.r-project.org/src/contrib/DBI_0.5-1.tar.gz https://cran.r-project.org/src/contrib/jsonlite_1.2.tar.gz \
	&& R CMD INSTALL DBI_0.5-1.tar.gz \
	&& R CMD INSTALL jsonlite_1.2.tar.gz \
	&& tar -xzf RPostgreSQL_0.4-1.tar.gz \
	&& chmod +x RPostgreSQL/configure \
	&& rm /RPostgreSQL/man/postgresqlSupport.Rd \
	&& R CMD INSTALL RPostgreSQL_0.4-1.tar.gz \
	&& echo 'install.packages("sqldf", repos="http://cran.uni-muenster.de/")' | R --no-save
# RPostgreSQL_0.4-1 is seriously f***ed up...

VOLUME /src /plots
WORKDIR /src

CMD [ "R" ]
