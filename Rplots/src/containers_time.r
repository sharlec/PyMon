source("db.r")

prepare_data = function(sys, i, field, x){
  sysdf = data.frame(date=fromJSON(sys$date[i]), load=fromJSON(sys[[field]][i]))
  sysdfLate = subset(x=sysdf, subset= date>start & date<end)
  return(sysdfLate)
}

plot_system = function (file, start, end, ymin, ymax, xlab, ylab, sys, field){
  png(file=file)
  plot(c(start,end), c(ymin, ymax), type="n", xlab=xlab, ylab=ylab, xaxt="n")
  axis.POSIXct(1,as.POSIXct(seq(start,end), origin="1970-01-01", by="minute"), format="%H:%M", las="2")
  lapply(
    seq(1,2), 
    function(i) lines(prepare_data(sys, i, field, data.frame(sys$docker_id[i])), col=i)
    # `data.frame(systems$server_id[i])` is needed to enforce evaluation of each iteration
  )
  #legend("topleft", legend=sys$docker_id, lty=c(1,1), col=c(seq(1, length(sys$docker_id))))
  dev.off()
}

#systems <- sqldf("select date_last from monitcollector_system", connection=connection)
#print(systems)
raw = sqldf(paste(readLines("containers_time.sql"),collapse=" "), connection=connection)

start = as.numeric(as.POSIXct("2017-03-16 10:10:00 CET"))
end = as.numeric(as.POSIXct("2017-03-16 13:10:00 CET"))

plot_system("container01.png", start, end, 0, 1, "Time", "CPU load", raw, "cpu")


#add_timestamp = function(containers, host, time){
#	
#
#plot_containers = function(i, x, raw, containers){
#	lapply(fromJSON(raw$date), function(timestamp) 
#}
#containers = data.frame()
#lapply(seq(1, length(raw$localhostname)), function(i) plot_containers(i, data.frame(raw$localhostname[i]), raw, containers))