from django.db import models
import xml.etree.ElementTree as ET
import json
import time
from django.conf import settings

monit_update_period = getattr(settings, 'MONIT_UPDATE_PERIOD', 60)
maximum_store_days = getattr(settings, 'MAXIMUM_STORE_DAYS', 7)

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
    tree = ET.fromstring(xml_str)
    if tree.find('.[@id]') is None:
        return False
    Server.update(tree)
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
            out_str += errors_messages[-i-1]
            ok = False
    if ok:
        return "running"
    return out_str


def json_list_append(json_list, value):
    try:
        new_list = json.loads(json_list)
        new_list.append(value)
    except:
        new_list = [value]
    # maximum allowed table size, if monit reports every monite, this stores data for one week
    maximum_table_length = int(maximum_store_days*24.*60.*60./monit_update_period)
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


def get_float(tree, xpath) -> float:
    float(tree.find(xpath).text)


class Server(models.Model):
    monit_id = models.CharField(max_length=32, unique=True)
    monit_version = models.TextField(null=True)
    localhostname = models.TextField(null=True)
    uptime = models.IntegerField(null=True)
    address = models.TextField(null=True)

    @classmethod
    def update(cls, tree):
        reporting_services = []
        root = tree.find('.[@id]')
        monit_id = root.get('id')
        server, created = cls.objects.get_or_create(monit_id=monit_id)
        server.monit_version = root.get("version")
        server.localhostname = root.find('./server/localhostname').text
        server.uptime = root.find('./server/uptime').text
        server.address = root.find('./server/httpd/address').text
        server.save()
        Platform.update(root, server)
        for service in root.findall('./services/service'):
            service_type = service.find("type").text
            service_name = service.find("type").text
            reporting_services.append(service_name)
            # properties for type=5 (system)
            if service_type == '5':
                System.update(service, server)
            # we call everything else a Process, not only type=3
            elif service_type == '8':
                Network.update(service,server)
            else:
                Process.update(service, server)
        remove_old_services(server, reporting_services)


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
    def update(cls, root, server):
        plat_xml = root.find('./platform')
        platform, created = Platform.objects.get_or_create(server=server)
        platform.name = plat_xml.find('name').text
        platform.release = plat_xml.find('release').text
        platform.version = plat_xml.find('version').text
        platform.machine = plat_xml.find('machine').text
        platform.cpu = plat_xml.find('cpu').text
        platform.memory = plat_xml.find('memory').text
        platform.swap = plat_xml.find('swap').text
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
    def update(cls, service, server):
        system, created = cls.objects.get_or_create(server=server)
        system.name = service.get("name")
        system.status = decode_status(int(service.find("status").text))
        system.status_hint = service.find("status_hint").text
        system.monitor = service.find("monitor").text
        system.monitormode = service.find("monitormode").text
        system.pendingaction = service.find("pendingaction").text
        if not service.find("system/load/avg01") is None:
            system.date_last = int(time.time())
            system.date = json_list_append(system.date, system.date_last)

            system.load_avg01_last = get_float(service, 'system/load/avg01')
            system.load_avg01 = json_list_append(system.load_avg01, system.load_avg01_last)
            system.load_avg05_last = get_float(service, 'system/load/avg05')
            system.load_avg05 = json_list_append(system.load_avg05, system.load_avg05_last)
            system.load_avg15_last = get_float(service, 'system/load/avg15')
            system.load_avg15 = json_list_append(system.load_avg15, system.load_avg15_last)
            system.cpu_user_last = get_float(service, 'system/cpu/user')
            system.cpu_user = json_list_append(system.cpu_user, system.cpu_user_last)
            system.cpu_system_last = get_float(service, 'system/cpu/system')
            system.cpu_system = json_list_append(system.cpu_system, system.cpu_system_last)
            system.cpu_wait_last = get_float(service, 'system/cpu/wait')
            system.cpu_wait = json_list_append(system.cpu_wait, system.cpu_wait_last)
            system.memory_percent_last = get_float(service, 'system/memory/percent')
            system.memory_percent = json_list_append(system.memory_percent, system.memory_percent_last)
            system.memory_kilobyte_last = get_float(service, 'system/memory/kilobyte')
            system.memory_kilobyte = json_list_append(system.memory_kilobyte, system.memory_kilobyte_last)
            system.swap_percent_last = get_float(service, 'system/swap/percent')
            system.swap_percent = json_list_append(system.swap_percent, system.swap_percent_last)
            system.swap_kilobyte_last = get_float(service, 'system/swap/kilobyte')
            system.swap_kilobyte = json_list_append(system.swap_kilobyte, system.swap_kilobyte_last)

        system.save()


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
    def update(cls, service, server):
        service_name = service.get("name")
        process, created = cls.objects.get_or_create(server=server, name=service_name)
        process.status = decode_status(int(service.find("status").text))
        process.status_hint = service.find("status_hint").text
        process.monitor = service.find("monitor").text
        process.monitormode = service.find("monitormode").text
        process.pendingaction = service.find("pendingaction").text
        if not service.find(".//cpu/percent") is None:
            process.pid = service.find('.//pid').text
            process.ppid = service.find('.//ppid').text
            process.uptime = service.find('.//uptime').text
            process.children = service.find('.//children').text
            # needs less characters than datetime.now().ctime() or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            process.date_last = int(time.time())
            process.date = json_list_append(process.date, process.date_last)
            process.cpu_percenttotal_last = get_float(service, './/cpu/percenttotal')
            process.cpu_percenttotal = json_list_append(process.cpu_percenttotal, process.cpu_percenttotal_last)
            process.memory_percenttotal_last = get_float(service, './/memory/percenttotal')
            process.memory_percenttotal = json_list_append(process.memory_percenttotal, process.memory_percenttotal_last)
            process.memory_kilobytetotal_last = int(get_float(service, './/memory/kilobytetotal'))
            process.memory_kilobytetotal = json_list_append(process.memory_kilobytetotal, process.memory_kilobytetotal_last)
        process.save()


class Network(Service):
    server = models.ForeignKey(Server)
    state = models.IntegerField(null=True)
    speed = models.IntegerField(null=True)
    duplex= models.IntegerField(null=True)       # TODO: boolean?

    download_packets_now = models.IntegerField(null=True)
    download_packets_total = models.IntegerField(null=True)
    download_bytes_now = models.IntegerField(null=True)
    download_bytes_total = models.IntegerField(null=True)
    download_errors_now = models.IntegerField(null=True)
    download_errors_total = models.IntegerField(null=True)

    upload_packets_now = models.IntegerField(null=True)
    upload_packets_total = models.IntegerField(null=True)
    upload_bytes_now = models.IntegerField(null=True)
    upload_bytes_total = models.IntegerField(null=True)
    upload_errors_now = models.IntegerField(null=True)
    upload_errors_total = models.IntegerField(null=True)

    @classmethod
    def update(cls, service, server):
        service_name = service.get("name")
        network, created = cls.objects.get_or_create(server=server, name=service_name)
        network.status = decode_status(int(service.find("status").text))
        network.status_hint = service.find("status_hint").text
        network.monitor = service.find("monitor").text
        network.monitormode = service.find("monitormode").text
        network.pendingaction = service.find("pendingaction").text

        if not service.find("link/state") is None:
            network.state = service.find('link/state').text
            network.speed = service.find('link/speed').text
            network.duplex = service.find('link/duplex').text
            network.download_packets_now = service.find('link/download/packets/now').text
            network.download_packets_total = service.find('link/download/packets/total').text
            network.download_bytes_now = service.find('link/download/bytes/now').text
            network.download_bytes_total = service.find('link/download/bytes/total').text
            network.download_errors_now = service.find('link/download/errors/now').text
            network.download_errors_total = service.find('link/download/errors/total').text
            network.upload_packets_now = service.find('link/upload/packets/now').text
            network.upload_packets_total = service.find('link/upload/packets/total').text
            network.upload_bytes_now = service.find('link/upload/bytes/now').text
            network.upload_bytes_total = service.find('link/upload/bytes/total').text
            network.upload_errors_now = service.find('link/upload/errors/now').text
            network.upload_errors_total = service.find('link/upload/errors/total').text

        network.save()

#
########## who needs groups? ##########

# service groups sind egal, da wird nur die tatsache gespeichert dass es diese gruppen gibt
# for servicegroup in xmldoc.getElementsByTagName('servicegroups')[0].getElementsByTagName('servicegroup'):
#   servicegroup_name = get_value(servicegroup, "", "", "name")
#   for service in servicegroup.getElementsByTagName('service'):
#     service_name = get_value(service)
#     print servicegroup_name, service_name
