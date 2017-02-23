
system <- sqldf("select * from monitcollector_system", connection=connection)

plot_sys<-function(i, x, a){
	png(file=paste("/tmp/r/",as.character(i),".png",sep=""))
	dates <- fromJSON(a$date[i])
	plot(dates, fromJSON(a$load_avg01[i]))
	axis.POSIXct(1,as.POSIXct(dates, origin="1970-01-01"), format="%Y-%m-%d %H:%M:%S")
	dev.off()
}

lapply(seq(1,length(system$server_id)), function(i) plot_sys(i, data.frame(system$server_id[i]), system))