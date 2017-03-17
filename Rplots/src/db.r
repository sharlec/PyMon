#install.packages("RPostgreSQL")
#install.packages("jsonlite")
#install.packages("sqldf")

require("RPostgreSQL")
require("sqldf")
require("jsonlite")


monit_db <- function(host="localhost", port=5432, dbname="pymonit", user="postgres", password="postgres"){
  driver <- dbDriver("PostgreSQL")
  connection <- dbConnect(driver, dbname=dbname, host=host, port=port, user=user, password=password)
  return(connection)
}

if (!exists("connection"))
  connection <- monit_db()
