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

connection <- monit_db("141.13.92.2")
tables <- sqldf("select * from  information_schema.tables", connection=connection)
system <- sqldf("select * from monitcollector_system", connection=connection)
json <- fromJSON(system$date[1])
