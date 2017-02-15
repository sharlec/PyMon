#install.packages("RPostgreSQL")
#install.packages("jsonlite")
#install.packages("sqldf")

require("RPostgreSQL")
require("sqldf")
require("jsonlite")


monit_db <- function(host="172.20.0.2", port=5432, dbname="pymonit", user="postgres", password="postgres"){
  driver <- dbDriver("PostgreSQL")
  connection <- dbConnect(driver, dbname=dbname, host=host, port=port, user=user, password=password)
  return(connection)
}

connection <- monit_db()
#tables <- sqldf("select * from  information_schema.tables", connection=connection)

# plot number of containers/host
containers <- sqldf("SELECT    monitcollector_server.localhostname,    COUNT(monitcollector_container.name) FROM    public.monitcollector_system,    public.monitcollector_server,    public.monitcollector_process,    public.monitcollector_service,    public.monitcollector_container WHERE    monitcollector_server.id = monitcollector_system.server_id AND   monitcollector_server.id = monitcollector_process.server_id AND   monitcollector_service.id = monitcollector_process.service_ptr_id AND   monitcollector_container.process_id = monitcollector_process.service_ptr_id GROUP BY monitcollector_server.localhostname ORDER BY   monitcollector_server.localhostname ASC; ", connection=connection)
pdf(file="containers.pdf")
barplot(containers$count, names=containers$localhostname)
dev.off()

system <- sqldf("select * from monitcollector_system", connection=connection)
#json <- fromJSON(system$date[1])


loads <- sapply(system$load_avg01, function(list) fromJSON(list))
dates <- sapply(system$date, function(list) ((fromJSON(list))))
pdf(file="host1.pdf")
plot(dates[[1]],loads[[1]],type="l")
dev.off()
