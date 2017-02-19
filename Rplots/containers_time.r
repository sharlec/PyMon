source("db.r")

#systems <- sqldf("select date_last from monitcollector_system", connection=connection)
#print(systems)
raw = sqldf(paste(readLines("containers_time.sql"),collapse=" "), connection=connection)

add_timestamp = function(containers, host, time){
	

plot_containers = function(i, x, raw, containers){
	lapply(fromJSON(raw$date), function(timestamp) 
}
containers = data.frame()
lapply(seq(1, length(raw$localhostname)), function(i) plot_containers(i, data.frame(raw$localhostname[i]), raw, containers))