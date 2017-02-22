source("db.r")

prepare_data = function(sys, i, field, x){
	sysdf = data.frame(date=fromJSON(sys$date[i]), load=fromJSON(sys[[field]][i]))
	sysdfLate = subset(x=sysdf, subset= date>start & date<end)
	return(sysdfLate)
}

plot_system = function (file, start, end, ymin, ymax, xlab, ylab, sys, field){
	png(file=file)
	plot(c(start,end), c(ymin, ymax), type="n", xlab=xlab, ylab=ylab)
	axis.POSIXct(1,as.POSIXct(seq(start,end), origin="1970-01-01"), format="%Y-%m-%d %H:%M:%S")
	lapply(
		seq(1,length(sys$server_id)), 
		function(i) lines(prepare_data(sys, i, field, data.frame(sys$server_id[i])), col=i)
		# `data.frame(systems$server_id[i])` is needed to enforce evaluation of each iteration
	)
	legend("topleft", legend=paste(sys$localhostname, sys$name), lty=c(1,1), col=c(seq(1, length(sys$server_id))))
	dev.off()
}


raw = sqldf(paste(readLines("processes.sql"),collapse=" "), connection=connection)

# unix -> Date: as.POSIXct(timestamp, origin="1970-01-01")
# Date -> unix: as.numeric(as.POSIXct("2017-02-19 17:51:17 CET"))
# current: as.numeric(Sys.time())
start_max = as.numeric(as.POSIXct("2017-02-03 18:00:00 CET"))
end_max = as.numeric(as.POSIXct("2017-02-08 12:00:00 CET"))
start = start
end = end
#start = as.numeric(as.POSIXct("2017-02-06 17:53:20 CET"))
#end = as.numeric(as.POSIXct("2017-02-07 21:40:00 CET"))

plot_system("proc_cpu.png", start, end, 0, 20, "Time", "cpu %", raw, "cpu_percenttotal")
plot_system("proc_mem.png", start, end, 0, 5, "Time", "mem %", raw, "memory_percenttotal")
plot_system("proc_memkb.png", start, end, 0, 32*1024, "Time", "mem kb", raw, "memory_kilobytetotal")
#plot_system("hosts_memkb.png", start, end, 0, 2*1024*1024, "Time", "Memory (kB)", systems, "memory_kilobyte")
#plot_system("hosts_swapkb.png", start, end, 0, 2*1024*1024, "Time", "Swap (kB)", systems, "swap_kilobyte")
#plot_system("hosts_cpuuser.png", start, end, 0, 100, "Time", "CPU (user)", systems, "cpu_user")
#plot_system("hosts_cpusystem.png", start, end, 0, 100, "Time", "CPU (system)", systems, "cpu_system")
#plot_system("hosts_cpuwait.png", start, end, 0, 100, "Time", "CPU (wait)", systems, "cpu_wait")
