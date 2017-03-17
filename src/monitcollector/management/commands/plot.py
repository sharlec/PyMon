from django.core.management.base import BaseCommand, CommandError

from monitcollector import models

import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict, OrderedDict
import json
from datetime import datetime

COLORS = ['r', 'g', 'b', 'y', 'm']


class Command(BaseCommand):
	help = '....'

	def add_arguments(self, parser):
		parser.add_argument('plot', nargs='+', choices=plots)
		parser.add_argument("--metric", "-m", choices=('cpu', 'memory'), default="cpu")
		parser.add_argument("--start", "-s", help="e.g. 'Mon Feb  6 08:43:20 2017'")
		parser.add_argument("--end", "-e", help="e.g. 'Mon Feb  6 08:46:26 2017'")
		parser.add_argument("--startstamp", "-st", type=float, default=1483225200,
							help="timestamp alternative to --start")
		parser.add_argument("--endstamp", "-et", type=float, default=datetime.timestamp(datetime.now()),
							help="timestamp alternative to --end")
		parser.add_argument("--host")
		parser.add_argument("--labels", "-l", action="store_true")
		parser.add_argument("--percent", "-p", action="store_true")
		parser.add_argument("--short", action="store_true")
		parser.add_argument("--filter", "-f", nargs="+")
		parser.add_argument("--outfile", "-o")
		pass

	def handle(self, *args, **options):
		if options['start']:
			options['start'] = datetime.timestamp(datetime.strptime(options['start'], "%c"))
		elif options['startstamp']:
			options['start'] = options['startstamp']
		if options['end']:
			options['end'] = datetime.timestamp(datetime.strptime(options['end'], "%c"))
		elif options['endstamp']:
			options['end'] = options['endstamp']
		print("Start: " + datetime.strftime(datetime.fromtimestamp(options['start']), "%c"))
		print("End: " + datetime.strftime(datetime.fromtimestamp(options['end']), "%c"))
		for plot in options['plot']:
			if plot in plots:
				plots[plot](options)
			else:
				print("unknown plot " + str(plot))


def containers_time(options):
	hosts = defaultdict(lambda: defaultdict(lambda: 0))
	for sys in models.System.objects.all():
		srv = models.Server.objects.get(system=sys)
		containers = models.Container.objects.filter(process__server=srv)
		for c in containers:
			if not c.date:
				continue
			for t in json.loads(c.date):
				hosts[srv.localhostname][t] += 1
	data = []
	for host in hosts:
		values = {"x": [], "y": []}
		for i in sorted(hosts[host]):
			y = hosts[host][i]
			if y == 0:
				continue
			values["x"].append(i)
			values["y"].append(y)
		data.append({"label": host, "data": values})
	print(len(data))
	for xyl in data:
		plt.plot(xyl["data"]["x"], xyl["data"]["y"], c=COLORS[data.index(xyl)], label=xyl["label"])
	# plt.scatter(xyl["data"]["x"], xyl["data"]["y"], c=COLORS[data.index(xyl)], label=xyl["label"])
	plt.show()


def container_bar(options):
	if options['filter']:
		systems = list(models.System.objects.filter(server__localhostname__in=options['filter']))
	else:
		systems = list(models.System.objects.filter())
	names = list(OrderedDict.fromkeys([system.server.localhostname for system in systems]))
	container_names = []
	n = len(names)
	data = []
	count = defaultdict(lambda: 0)
	for container in models.Container.objects.all():
		if container.date is None or container.cpu is None:
			continue
		array = np.array([0] * n)
		cdates = json.loads(container.date)
		if options['metric'] is "cpu":
			values = json.loads(container.cpu)
		else:
			values = json.loads(container.memory)
		filtered = filter_date(cdates, values, options['start'], options['end'])
		if not len(filtered) > 0:
			continue
		for system in systems:
			if container.process.server == system.server:
				mean = np.mean(filtered)
				if np.isnan(mean):
					mean = 0
				index = names.index(system.server.localhostname)
				array[index] = mean
				count[index] += 1
		data.append(array)
		container_names.append(container.name)
	if not options['labels']:
		container_names = None
	width = .35
	barplot(n, names, data, width, legends=container_names)
	plt.ylabel("Containers")
	plt.xlabel("Hosts")
	plt.yticks([], [])
	plt.title("Containers * " + options['metric'].upper())
	if options["outfile"]:
		plt.savefig(options['outfile'])
	else:
		plt.show()


def filter_date(dates, values, start, end):
	result = []
	for i, t in enumerate(dates):
		if start < t < end:
			result.append(values[i])
	return result


def barplot(n, names, data, width, legends=None, ylen=None):
	ind = np.arange(n)
	ps = []
	for i in range(0, len(data)):
		ps.append(plt.bar(ind, data[i], width, bottom=sum(data[:i]), color=np.random.rand(3, 1)))
	plt.xticks(ind, names)
	if ylen:
		plt.yticks(np.arange(ylen, step=ylen))
	if legends:
		plt.legend(ps, legends)
	pass


def pie_host(options):
	if not options['host']:
		host = "pine64"
	else:
		host = options['host']

	system = models.System.objects.filter(server__localhostname=host)
	data = []
	names = []
	for container in models.Container.objects.filter(process__server__system=system):
		if container.date is None or container.cpu is None:
			continue
		cdates = json.loads(container.date)
		if options['metric'] is "cpu":
			values = json.loads(container.cpu)
		else:
			values = json.loads(container.memory)
		filtered = filter_date(cdates, values, options['start'], options['end'])
		if not len(filtered) > 0:
			continue
		mean = np.mean(filtered)
		if np.isnan(mean):
			mean = 0
		data.append(mean)
		name = container.name
		if options['short']:
			if "_" in name:
				name = name.split("_")[-2]
			else:
				name = name[-8:]
		names.append(name)
	if not options['labels']:
		names = [""] * len(data)
	autopct = "%1.1f%%"
	if not options['percent']:
		autopct = ""
	plt.pie(data, labels=names, autopct=autopct)
	plt.title(
		"Containers average " + options['metric'].upper() + " percent (relative) on " + host)
	if options["outfile"]:
		plt.savefig(options['outfile'])
	else:
		plt.show()


plots = {
	"container_time": containers_time,
	"container": container_bar,  # container* cpu per host, limited through time; options: -s -e
	"pie_host": pie_host,  # options: -s -e, --host, -p, -l, --short
}


# examples:

# python3 ./manage.py plot container -m cpu -f node-1 node-2 node-3
# python3 ./manage.py plot container -m memory -f node-1 node-2 node-3
# python3 ./manage.py plot container -m cpu -st 1486367000 -et 1486367186
# python3 ./manage.py plot container -m cpu -s 'Mon Feb 6 08:43:20 2017' -e 'Mon Feb 6 08:46:26 2017'
# python3 ./manage.py plot container -o /tmp/bar.png

# python3 ./manage.py plot pie_host --host master -m memory -p -l --short
# python3 ./manage.py plot pie_host --host master -m cpu
# python3 ./manage.py plot pie_host --host pine64 -m cpu -p -l --short
