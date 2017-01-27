from django.db import models
from xml.dom import minidom
from lxml import etree as ET
import json
import time
from django.conf import settings
import logging

log = logging.getLogger(__name__)

monit_update_period = getattr(settings, 'MONIT_UPDATE_PERIOD', 60)
maximum_store_days = getattr(settings, 'MAXIMUM_STORE_DAYS', 7)
CONTAINER_METRICS = set(("cpu", "memory"))

"""
from the monit source code (monit/contrib/wap.php):
//For conversion of status codes to text
$event[0] = 'OK';
$event[1] = 'Checksum failed';
$event[2] = 'Resource limit matched';
$event[4] = 'Timeout';
$event[8] = 'Timestamp failed';
$event[16] = 'Size failed';
$event[32] = 'Connection failed';
$event[64] = 'Permission failed';
$event[128] = 'UID failed';
$event[256] = 'GID failed';
$event[512] = 'Does not exist';
$event[1024] = 'Invalid type';
$event[2048] = 'Data access error';
$event[4096] = 'Execution failed';
$event[8192] = 'Changed';
$event[16384] = 'ICMP failed';
$monitored[0] = 'No';
$monitored[1] = 'Yes';
$monitored[2] = 'Init';
"""


def collect_data(xml_str):
	# only ready data if it has a monit id
	try:
		tree = ET.fromstring(xml_str)
		monit_id = getVal(tree, "@id", True)
	except:
		return False
	Server.update(tree, monit_id)
	return True


def decode_status(status):
	errors_messages = [
		'Ok',
		'Checksum failed',
		'Resource limit matched',
		'Timeout',
		'Timestamp failed',
		'Size failed',
		'Connection failed',
		'Permission failed',
		'UID failed',
		'GID failed',
		'Does not exist',
		'Invalid type',
		'Data access error',
		'Execution failed',
		'Filesystem flags failed',
		'ICMP failed',
		'Content failed',
		'Monit instance failed',
		'Action done',
		'PID failed',
		'PPID failed',
		'Heartbeat failed',
		'Status failed',
		'Uptime failed',
		'Link down',
		'Speed failed',
		'Saturation exceeded',
		'Download bytes exceeded',
		'Upload bytes exceeded',
		'Download packets exceeded',
		'Upload packets exceeded'
	]

	# choice_monitor = ['No', 'Yes', 'Init']
	# format to a bitarray
	bits = '{0:030b}'.format(status)
	out_str = ''
	ok = True
	for i in range(len(bits)):
		if bits[i] == "1":
			if not ok:
				out_str += ", "
			out_str += errors_messages[-i - 1]
			ok = False
	if ok:
		return "running"
	return out_str


def getVal(xmldoc, expression, isAttribute=False):
    try:
        path = ET.XPath(expression)
        count = ET.XPath('count(%s)' % expression)
        if isAttribute:
            if count(xmldoc) > 1:
                val = path(xmldoc)
            else:
                val = path(xmldoc)[0]
        else:
            if count(xmldoc) > 1:
                val = path(xmldoc)
            else:
                val = path(xmldoc)[0].text
        return val
    except:
        return None


def json_list_append(json_list, value):
	log.debug("append " + str(value) + " to " + str(json_list))
	try:
		new_list = json.loads(json_list)
		new_list.append(value)
	except:
		new_list = [value]
	# maximum allowed table size, if monit reports every monite, this stores data for one week
	maximum_table_length = int(maximum_store_days * 24. * 60. * 60. / monit_update_period)
	# just remove the first one, should be better in future
	if len(new_list) > maximum_table_length:
		new_list = new_list[-int(maximum_table_length):]
	return json.dumps(new_list)


def remove_old_services(server, service_list):
	if server.system.name not in service_list:
		server.system.delete()
	processes = server.process_set.all()
	for process in processes:
		if process.name not in service_list:
			process.delete()


def parse_docker_json(json_str):
	log.error("JSON:" + json_str)
	if json is None:
		return []
	struct = json.loads(json_str)
	containers = []
	for c in struct:
		containers.append(struct[c])
	return containers


class Server(models.Model):
	monit_id = models.CharField(max_length=32, unique=True)
	monit_version = models.TextField(null=True)
	localhostname = models.TextField(null=True)
	uptime = models.IntegerField(null=True)
	address = models.TextField(null=True)

	@classmethod
	def update(cls, xmldoc, monit_id):
		log.info("updating server")
		reporting_services = []
		server, created = cls.objects.get_or_create(monit_id=monit_id)
		server.monit_version = getVal(xmldoc, "@version", True)

		server.localhostname = getVal(xmldoc, "./server/localhostname")
		server.uptime = getVal(xmldoc, "./server/uptime")
		server.address = getVal(xmldoc, "./server/address")
		server.save()
		Platform.update(xmldoc, server)

		for service in getVal(xmldoc, "services/service"):
			service_type = getVal(service, "type")
			service_name = getVal(service, "@name", True)
			reporting_services.append(service_name)
			# properties for type=5 (system)
			if service_type == '5':
				System.update(server, service)
			# we call everything else a Process, not only type=3
			elif service_type == '8':
				Network.update(server, service)
			else:
				Process.update(server, service)
		remove_old_services(server, reporting_services)

	def __str__(self):
		return self.localhostname


class Platform(models.Model):
    server = models.OneToOneField('Server')
    name = models.TextField(null=True)
    release = models.TextField(null=True)
    version = models.TextField(null=True)
    machine = models.TextField(null=True)
    cpu = models.IntegerField(null=True)
    memory = models.IntegerField(null=True)
    swap = models.IntegerField(null=True)
    @classmethod
    def update(cls, xmldoc, server):
        platform, created = Platform.objects.get_or_create(server=server)
        platform.name = getVal(xmldoc, "platform/name")
        platform.release = getVal(xmldoc, "platform/release")
        platform.version = getVal(xmldoc, "platform/version")
        platform.machine = getVal(xmldoc, "platform/machine")
        platform.cpu = getVal(xmldoc, "platform/cpu")
        platform.memory = getVal(xmldoc, "platform/memory")
        platform.swap = getVal(xmldoc, "platform/swap")
        platform.save()


# Service
class Service(models.Model):
	# not unique since there could be multiple server with service 'nginx', etc.
	name = models.TextField()
	status = models.TextField(null=True)
	status_hint = models.IntegerField(null=True)
	monitor = models.IntegerField(null=True)
	monitormode = models.IntegerField(null=True)
	pendingaction = models.IntegerField(null=True)

	def __str__(self):
		return self.name


# Service type=5
class System(Service):
	server = models.OneToOneField('Server')
	date_last = models.PositiveIntegerField(null=True)
	date = models.TextField(null=True)
	load_avg01_last = models.FloatField(null=True)
	load_avg01 = models.TextField(null=True)
	load_avg05_last = models.FloatField(null=True)
	load_avg05 = models.TextField(null=True)
	load_avg15_last = models.FloatField(null=True)
	load_avg15 = models.TextField(null=True)
	cpu_user_last = models.FloatField(null=True)
	cpu_user = models.TextField(null=True)
	cpu_system_last = models.FloatField(null=True)
	cpu_system = models.TextField(null=True)
	cpu_wait_last = models.FloatField(null=True)
	cpu_wait = models.TextField(null=True)
	memory_percent_last = models.FloatField(null=True)
	memory_percent = models.TextField(null=True)
	memory_kilobyte_last = models.PositiveIntegerField(null=True)
	memory_kilobyte = models.TextField(null=True)
	swap_percent_last = models.FloatField(null=True)
	swap_percent = models.TextField(null=True)
	swap_kilobyte_last = models.PositiveIntegerField(null=True)
	swap_kilobyte = models.TextField(null=True)

	@classmethod
	def update(cls, server, service):
		system, created = cls.objects.get_or_create(server=server)
		system.name = getVal(service, "@name",True)
		system.status = decode_status(int(getVal(service, "status")))
		system.status_hint = getVal(service, "status_hint")
		system.monitor = getVal(service, "monitor")
		system.monitormode = getVal(service, "monitormode")
		system.pendingaction = getVal(service, "pendingaction")
		if not getVal(service, "system/load/avg01") is None:
			system.date_last = int(time.time())
			system.date = json_list_append(system.date, system.date_last)
			system.load_avg01_last = float(getVal(service, "system/load/avg01"))
			system.load_avg01 = json_list_append(system.load_avg01, system.load_avg01_last)
			system.load_avg05_last = float(getVal(service, "system/load/avg05"))
			system.load_avg05 = json_list_append(system.load_avg05, system.load_avg05_last)
			system.load_avg15_last = float(getVal(service, "system/load/avg15"))
			system.load_avg15 = json_list_append(system.load_avg15,  system.load_avg15_last)
			system.cpu_user_last = float(getVal(service, "system/cpu/user"))
			system.cpu_user = json_list_append(system.cpu_user, system.cpu_user_last)
			system.cpu_system_last = float(getVal(service, "system/cpu/system"))
			system.cpu_system = json_list_append(system.cpu_system, system.cpu_system_last)
			system.cpu_wait_last = float(getVal(service, "system/cpu/wait"))
			system.cpu_wait = json_list_append(system.cpu_wait, system.cpu_wait_last)
			system.memory_percent_last = float(getVal(service, "system/memory/percent"))
			system.memory_percent = json_list_append(system.memory_percent, system.memory_percent_last)
			system.memory_kilobyte_last = int(getVal(service, "system/memory/kilobyte"))
			system.memory_kilobyte = json_list_append(system.memory_kilobyte, system.memory_kilobyte_last)
			system.swap_percent_last = float(getVal(service, "system/swap/percent"))
			system.swap_percent = json_list_append(system.swap_percent, system.swap_percent_last)
			system.swap_kilobyte_last = int(getVal(service, "system/swap/kilobyte"))
			system.swap_kilobyte = json_list_append(system.swap_kilobyte, system.swap_kilobyte_last)
		system.save()



class Container(models.Model):
	process = models.ForeignKey("Process")
	name = models.TextField()
	docker_id = models.TextField()
	image = models.TextField()
	state = models.TextField()
	status = models.TextField()

	date_last = models.PositiveIntegerField(null=True)
	date = models.TextField(null=True)
	cpu_last = models.FloatField(null=True)
	cpu = models.TextField(null=True)
	memory_last = models.FloatField(null=True)
	memory = models.TextField(null=True)

	@classmethod
	def update(cls, stat, process):
		container_id = stat['id']
		log.debug("add container " + str(container_id))
		container, created = cls.objects.get_or_create(process=process, docker_id=container_id)
		if created:
			container.name = stat['name']
			container.image = stat['image']
		container.state = stat['state']
		container.status = stat['status']
		if CONTAINER_METRICS <= stat['stats'].keys():
			container.date_last = int(time.time())
			container.date = json_list_append(container.date, container.date_last)
			container.cpu_last = stat['stats']['cpu']
			container.cpu = json_list_append(container.cpu, container.cpu_last)
			container.memory_last = stat['stats']['memory']
			container.memory = json_list_append(container.memory, container.memory_last)
		container.save()
		log.debug("done with " + str(container_id))

	def __str__(self):
		return self.name


# we call everything else a Process, not only type=3
class Process(Service):
	server = models.ForeignKey('Server')
	date_last = models.PositiveIntegerField(null=True)
	date = models.TextField(null=True)
	pid = models.IntegerField(null=True)
	ppid = models.IntegerField(null=True)
	uptime = models.PositiveIntegerField(null=True)
	children = models.PositiveIntegerField(null=True)
	cpu_percenttotal_last = models.FloatField(null=True)
	cpu_percenttotal = models.TextField(null=True)
	memory_percenttotal_last = models.FloatField(null=True)
	memory_percenttotal = models.TextField(null=True)
	memory_kilobytetotal_last = models.PositiveIntegerField(null=True)
	memory_kilobytetotal = models.TextField(null=True)

	@classmethod
	def update(cls, server, service):
		service_name = getVal(service, "@name",True)
		process, created = cls.objects.get_or_create(server=server,name=service_name)
		process.status = decode_status(int(getVal(service, "status")))
		process.status_hint = getVal(service, "status_hint")
		process.monitor = getVal(service, "monitor")
		process.monitormode = getVal(service, "monitormode")
		process.pendingaction = getVal(service, "pendingaction")
		if not getVal(service, "cpu/percent") is None:
			process.pid = getVal(service, "pid")
			process.ppid = getVal(service, "ppid")
			process.uptime = getVal(service, "uptime")
			process.children = getVal(service, "children")
			# needs less characters than datetime.now().ctime() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			process.date_last = int(time.time())
			process.date = json_list_append(process.date, process.date_last)
			process.cpu_percenttotal_last = float(getVal(service, "cpu/percenttotal"))
			process.cpu_percenttotal = json_list_append(process.cpu_percenttotal, process.cpu_percenttotal_last)
			process.memory_percenttotal_last = float(getVal(service, "memory/percenttotal"))
			process.memory_percenttotal = json_list_append(process.memory_percenttotal, process.memory_percenttotal_last)
			process.memory_kilobytetotal_last = int(getVal(service, "memory/kilobytetotal"))
			process.memory_kilobytetotal = json_list_append(process.memory_kilobytetotal, process.memory_kilobytetotal_last)

		if service_name == "docker-containers" and not getVal(service, "program/output") is None:
			stats = parse_docker_json(getVal(service, "program/output"))
			log.info("%i: %s", len(stats), stats)
			for s in stats:
				log.debug(s)
				Container.update(s, process)
		else:
			log.info("no docker containers " + str(service_name))
		process.save()

	def __str__(self):
		return self.name


class Network(Service):
	# TODO: history of these fields?
	server = models.ForeignKey(Server)
	state = models.IntegerField(null=True)
	speed = models.IntegerField(null=True)
	duplex = models.IntegerField(null=True)  # TODO: boolean?

	download_packets_now_last = models.IntegerField(null=True)
	download_packets_now = models.TextField(null=True)
	download_packets_total_last = models.IntegerField(null=True)
	download_packets_total = models.TextField(null=True)
	download_bytes_now_last = models.IntegerField(null=True)
	download_bytes_now = models.TextField(null=True)
	download_bytes_total_last = models.IntegerField(null=True)
	download_bytes_total = models.TextField(null=True)
	download_errors_now_last = models.IntegerField(null=True)
	download_errors_now = models.TextField(null=True)
	download_errors_total_last = models.IntegerField(null=True)
	download_errors_total = models.TextField(null=True)
	upload_packets_now_last = models.IntegerField(null=True)
	upload_packets_now = models.TextField(null=True)
	upload_packets_total_last = models.IntegerField(null=True)
	upload_packets_total = models.TextField(null=True)
	upload_bytes_now_last = models.IntegerField(null=True)
	upload_bytes_now = models.TextField(null=True)
	upload_bytes_total_last = models.IntegerField(null=True)
	upload_bytes_total = models.TextField(null=True)
	upload_errors_now_last = models.IntegerField(null=True)
	upload_errors_now = models.TextField(null=True)
	upload_errors_total_last = models.IntegerField(null=True)
	upload_errors_total = models.TextField(null=True)

	@classmethod
	def update(cls, server, service):
		service_name = getVal(service, "@name", True)
		network, created = cls.objects.get_or_create(server=server, name=service_name)
		network.status = decode_status(int(getVal(service, "status")))
		network.status_hint = getVal(service, "status_hint")
		network.monitor = getVal(service, "monitor")
		network.monitormode = getVal(service, "monitormode")
		network.pendingaction = getVal(service, "paddingaction")

		if not getVal(service, "link/state") is None:

			network.state = int(getVal(service, "link/state"))
			network.speed =int(getVal(service, "link/speed"))
			network.duplex = int(getVal(service, "link/duplex"))
			network.download_packets_now_last = int(getVal(service, "link/download/packets/now"))
			network.download_packets_now = json_list_append(network.download_packets_now,
															network.download_packets_now_last)
			network.download_packets_total_last = int(getVal(service, 'link/download/packets/total'))
			network.download_packets_total = json_list_append(network.download_packets_total,
															  network.download_packets_total_last)
			network.download_bytes_now_last = int(getVal(service, 'link/download/bytes/now'))
			network.download_bytes_now = json_list_append(network.download_bytes_now, network.download_bytes_now_last)
			network.download_bytes_total_last = int(getVal(service, 'link/download/bytes/total'))
			network.download_bytes_total = json_list_append(network.download_bytes_total,
															network.download_bytes_total_last)
			network.download_errors_now_last = int(getVal(service, 'link/download/errors/now'))
			network.download_errors_now = json_list_append(network.download_errors_now,
														   network.download_errors_now_last)
			network.download_errors_total_last = int(getVal(service, 'link/download/errors/total'))
			network.download_errors_total = json_list_append(network.download_errors_total,
															 network.download_errors_total_last)
			network.upload_packets_now_last = int(getVal(service, 'link/upload/packets/now'))
			network.upload_packets_now = json_list_append(network.upload_packets_now, network.upload_packets_now_last)
			network.upload_packets_total_last = int(getVal(service, 'link/upload/packets/total'))
			network.upload_packets_total = json_list_append(network.upload_packets_total,
															network.upload_packets_total_last)
			network.upload_bytes_now_last = int(getVal(service, 'link/upload/bytes/now'))
			network.upload_bytes_now = json_list_append(network.upload_bytes_now, network.upload_bytes_now_last)
			network.upload_bytes_total_last = int(getVal(service, 'link/upload/bytes/total'))
			network.upload_bytes_total = json_list_append(network.upload_bytes_total, network.upload_bytes_total_last)
			network.upload_errors_now_last = int(getVal(service, 'link/upload/errors/now'))
			network.upload_errors_now = json_list_append(network.upload_errors_now, network.upload_errors_now_last)
			network.upload_errors_total_last = int(getVal(service, 'link/upload/errors/total'))
			network.upload_errors_total = json_list_append(network.upload_errors_total,
														   network.upload_errors_total_last)

		network.save()

#
########## who needs groups? ##########

# service groups sind egal, da wird nur die tatsache gespeichert dass es diese gruppen gibt
# for servicegroup in xmldoc.getElementsByTagName('servicegroups')[0].getElementsByTagName('servicegroup'):
#   servicegroup_name = get_value(servicegroup, "", "", "name")
#   for service in servicegroup.getElementsByTagName('service'):
#     service_name = get_value(service)
#     print servicegroup_name, service_name
