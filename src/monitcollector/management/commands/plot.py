from django.core.management.base import BaseCommand, CommandError

from monitcollector import models

import matplotlib.pyplot as plt
from collections import defaultdict
import json

COLORS = ['r', 'g', 'b', 'y', 'm']


class Command(BaseCommand):
	help = '....'

	def add_arguments(self, parser):
		# parser.add_argument('poll_id', nargs='+', type=int)
		pass

	def handle(self, *args, **options):
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
			#plt.scatter(xyl["data"]["x"], xyl["data"]["y"], c=COLORS[data.index(xyl)], label=xyl["label"])
		plt.show()
