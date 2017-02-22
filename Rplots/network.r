source("db.r")

prepare_data = function(sys, i, field, x){
	values = fromJSON(sys[[field]][i])
	sysdf = data.frame(seq(1, length(values)), load=values)
	return(sysdf)
	#sysdfLate = subset(x=sysdf, subset= date>start & date<end)
	#return(sysdfLate)
}

plot_system = function (file, start, end, ymin, ymax, xlab, ylab, sys, field){
	png(file=file)
	plot(c(0,22500), c(ymin, ymax), type="n", xlab=xlab, ylab=ylab)
	#axis.POSIXct(1,as.POSIXct(seq(start,end), origin="1970-01-01"), format="%Y-%m-%d %H:%M:%S")
	lapply(
		seq(1,length(sys$server_id)), 
		function(i) lines(prepare_data(sys, i, field, data.frame(sys$server_id[i])), col=i)
		# `data.frame(systems$server_id[i])` is needed to enforce evaluation of each iteration
	)
	legend("topleft", legend=sys$localhostname, lty=c(1,1), col=c(seq(1, length(systems$server_id))))
	dev.off()
}


raw = sqldf(paste(readLines("network.sql"),collapse=" "), connection=connection)

# unix -> Date: as.POSIXct(timestamp, origin="1970-01-01")
# Date -> unix: as.numeric(as.POSIXct("2017-02-19 17:51:17 CET"))
# current: as.numeric(Sys.time())
start_max = as.numeric(as.POSIXct("2017-02-03 18:00:00 CET"))
end_max = as.numeric(as.POSIXct("2017-02-08 12:00:00 CET"))
start = start
end = end
#start = as.numeric(as.POSIXct("2017-02-06 17:53:20 CET"))
#end = as.numeric(as.POSIXct("2017-02-07 21:40:00 CET"))

plot_system("net_down.png", start, end, 0, 4000000, "\"Time\"", "net dl (bytes)", raw, "download_bytes_now")
plot_system("net_up.png", start, end, 0, 700000, "\"Time\"", "net up (bytes)", raw, "upload_bytes_now")