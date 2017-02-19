source("db.r")

#systems <- sqldf("select date_last from monitcollector_system", connection=connection)
#print(systems)
raw = sqldf(paste(readLines("containers_time.sql"),collapse=" "), connection=connection)

