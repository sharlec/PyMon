source("db.r")

systems <- sqldf("select monitcollector_server.localhostname,monitcollector_system.* from monitcollector_system, monitcollector_server WHERE monitcollector_server.id = monitcollector_system.server_id", connection=connection)

# unix -> Date: as.POSIXct(timestamp, origin="1970-01-01")
# Date -> unix: as.numeric(as.POSIXct("2017-02-19 17:51:17 CET"))
start = as.numeric(as.POSIXct("2017-02-06 17:53:20 CET"))
end = as.numeric(as.POSIXct("2017-02-07 21:40:00 CET"))
prepare_load_data01 = function(sys, i){
	sysdf = data.frame(date=fromJSON(sys$date[i]), load=fromJSON(sys$load_avg01[i]))
	sysdfLate = subset(x=sysdf, subset= date>start & date<end)
	return(sysdfLate)
}

plot_load01 = function(sys, i, x){
	lines(prepare_load_data01(sys, i), col=i, )
	axis.POSIXct(1,as.POSIXct(fromJSON(systems$date[i]), origin="1970-01-01"), format="%Y-%m-%d %H:%M:%S")
}

png(file="hosts_load01.png")
plot(c(start,end),c(0,10),type="n", xlab="Time",ylab="Load (Avg 1 min)")

lapply(seq(1,length(systems$server_id)), function(i) plot_load01(systems, i , data.frame(systems$server_id[i])))
legend("topleft", legend=systems$localhostname, lty=c(1,1), col=c(seq(1, length(systems$server_id))))

dev.off()
