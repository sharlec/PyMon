source("db.r")

prepare_data = function(sys, i, field, x){
	values = fromJSON(sys[[field]][i])
	#sysdf = data.frame(seq(1, length(values)), load=values)
	#return(sysdf)
	sysdf = data.frame(date=fromJSON(sys$date[i]), load=fromJSON(sys[[field]][i]))
	sysdfLate = subset(x=sysdf, subset= date>start & date<end)
	return(sysdfLate)
}


plot_system = function (file, start, end, ymin, ymax, xlab, ylab, sys, field){
	png(file=file, width=700, height=350)
	plot(c(start,end), c(ymin, ymax), type="n", xlab=xlab, ylab=ylab, xaxt="n")
	axis.POSIXct(1,as.POSIXct(seq(start,end), origin="1970-01-01", by="minute"), format="%H:%M", las="2")
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
start_max = as.numeric(as.POSIXct("2017-03-16 15:00:00 CET"))
end_max = as.numeric(as.POSIXct("2017-03-16 16:00:00 CET"))
start = start_max
end = end_max
#start = as.numeric(as.POSIXct("2017-02-06 17:53:20 CET"))
#end = as.numeric(as.POSIXct("2017-02-07 21:40:00 CET"))

plot_system("net_down.png", start, end, 0, 2000, "", "Download (bytes)", raw, "download_bytes_now")
plot_system("net_up.png", start, end, 0, 2000, "", "Upload (bytes)", raw, "upload_bytes_now")
