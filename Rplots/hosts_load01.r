source("db.r")

systems <- sqldf("select monitcollector_server.localhostname,monitcollector_system.* from monitcollector_system, monitcollector_server WHERE monitcollector_server.id = monitcollector_system.server_id", connection=connection)

# unix -> Date: as.POSIXct(timestamp, origin="1970-01-01")
# Date -> unix: as.numeric(as.POSIXct("2017-02-19 17:51:17 CET"))
start = as.numeric(as.POSIXct("2017-02-06 17:53:20 CET"))
end = as.numeric(as.POSIXct("2017-02-07 21:40:00 CET"))
prepare_load_data01 = function(sys, i, field){
	sysdf = data.frame(date=fromJSON(sys$date[i]), load=fromJSON(sys[[field]][i]))
	sysdfLate = subset(x=sysdf, subset= date>start & date<end)
	return(sysdfLate)
}

plot_load01 = function(sys, i, field, x){
	lines(prepare_load_data01(sys, i, field), col=i)
}

plot_system = function (file, start, end, ymin, ymax, xlab, ylab, sys, field, plot_fun){
	png(file=file)
	plot(c(start,end), c(ymin, ymax), type="n", xlab=xlab, ylab=ylab)
	axis.POSIXct(1,as.POSIXct(seq(start,end), origin="1970-01-01"), format="%Y-%m-%d %H:%M:%S")
	lapply(
		seq(1,length(sys$server_id)), 
		function(i) plot_fun(sys, i, field, data.frame(systems$server_id[i]))
	)
	legend("topleft", legend=systems$localhostname, lty=c(1,1), col=c(seq(1, length(systems$server_id))))
	dev.off()
}

plot_system("hosts_load01.png", start, end, 0, 10, "Time", "Load (avg 1 min)", systems, "load_avg01", plot_load01)

