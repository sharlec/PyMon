sysdf <- data.frame(date=fromJSON(system$date[1]), load=fromJSON(system$load_avg01[1]))
sysdfLate <- subset(x=sysdf, subset= date>1486400000)
sysdfLate2 <- subset(x=sysdf, subset= date>1486400000 & date<1486500000)
