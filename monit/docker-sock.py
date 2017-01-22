#!/usr/bin/python3

import http.server
import json
import logging
import socket
import socketserver
import statistics
import threading
import time

log = logging.getLogger(__name__)

PORT = 5000
MONITOR_STATUSES = ("running")

containers = {}
thread_map = {}

"""
Provide an HTTP-endpoint (/) to get preprocessed data from the Docker API.
The main thread handles HTTP (basic server reduces size), and coordinates Docker API consuming helper threads.
The helper threads connect to docker.sock, register for the stats-Stream of a container, and collect some information.
Metric data is stored and the mean of them is used on the endpoint.
Helper and main threads share the global "containers" with all metrics (but not the history).
When a stream times out, the helper stops.

calling the endpoint empties the history, adds new containers (creates helper threads), and removes stale containers (without helper thread, or stop helper thread).

Pretty-printed JSON is available under /pretty, without resetting history, but with adding and removing containers/threads

Using docker-py (https://github.com/docker/docker-py) would be quite nice, but stopping stale threads would be harder (generator without timeout; for-loop)
"""


def container_cpu_percent(stats):
	container_cpu = stats["cpu_stats"]["cpu_usage"]["total_usage"]
	pre_container_cpu = stats["precpu_stats"]["cpu_usage"]["total_usage"]
	system_cpu = stats["cpu_stats"]["system_cpu_usage"]
	pre_system_cpu = stats["precpu_stats"]["system_cpu_usage"]
	cpu = ((container_cpu - pre_container_cpu) / (system_cpu - pre_system_cpu)) * 100
	log.debug("((%f - %f) / (%f - %f)) * 100 = %f", container_cpu, pre_container_cpu, system_cpu, pre_system_cpu, cpu)
	return cpu


class StatThread(threading.Thread):
	def __init__(self, container):
		threading.Thread.__init__(self)
		self.id = container
		self.active = True
		self.__metrics = ("cpu", "memory")  # TODO network
		self.history = {}  # TODO: synchronize?
		self.init_history()

	def init_history(self):
		for m in self.__metrics:
			self.history[m] = []

	def update_stats(self, data):
		old = containers[self.id]["stats"]
		new = {
			"cpu": container_cpu_percent(data),
			"memory": data["memory_stats"]["usage"]
		}
		for m in self.__metrics:
			self.history[m].append(new[m])
			log.warn(m[1] + " history: " + str(len(self.history[m])) + " current: " + str(new[m]))
			new[m] = statistics.mean(self.history[m])
		containers[self.id]["stats"] = new

	def run(self):
		with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
			sock.connect("/var/run/docker.sock")
			sock.send(bytes("GET /containers/{id}/stats HTTP/1.0\r\n\n".format(id=self.id), 'utf8'))
			sock.settimeout(5)  # TODO an active container should have an update about every second
			while self.active:
				try:
					raw = sock.recv(16048)  # TODO: basic containers have around 2000 bytes
					http = raw.decode('utf8')
					content = http.split("\n")[-2]
					log.info(len(content))
					if len(content) > 1:
						data = json.loads(content)
						log.info("{}: {}".format(self.id[0:12], len(data)))
						self.update_stats(data)
				except socket.timeout:
					log.error("container {} timed out".format(self.id[0:12]))
					self.active = False


def iterate_containers():
	#TODO: get all containers ?all=True
	containers = {}
	with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
		c.connect("/var/run/docker.sock")
		c.send(bytes("GET /containers/json HTTP/1.0\r\n\n", 'ascii'))
		raw = c.recv(102400)  # TODO: sufficient for roughly 128 containers
		log.info("container list length: %s", len(raw))

		http = raw.decode('utf8')
		data = json.loads(http.split("\n")[-2])

		for meta in data:
			containers[meta["Id"]] = {
				"name": meta["Names"][0],
				"id": meta["Id"],
				#"ip": meta["NetworkSettings"]["Networks"]["bridge"]["IPAddress"],
				"image": meta["Image"],
				"state": meta["State"],
				"status": meta["Status"],
				"stats": {}
			}
			#TODO: uptime
	return containers


def manage_stat_threads():
	global containers
	stalled = []
	for t in thread_map:
		if t not in containers:
			thread_map[t].active = False
		if not thread_map[t].active:
			stalled.append(t)
	log.debug("stalled: " + str(stalled))
	for c in containers:
		if c not in thread_map:
			thread = StatThread(c)
			thread.start()
			thread_map[c] = thread
	for t in stalled:
		thread_map.pop(t)


def update_containers():
	new_containers = iterate_containers()
	for nc in new_containers:
		if nc not in containers:
			containers[nc] = new_containers[nc]
		else:
			for k in ("state","status"):
				containers[nc][k] = new_containers[nc][k]
	manage_stat_threads()


def update(reset=True):
	#TODO: send history as well?
	update_containers()
	data = dict(containers)
	for c in data:
		if c not in thread_map or not thread_map[c].active:
			containers.pop(c)
	if reset:
		for t in thread_map:
			thread_map[t].init_history()
	return data


def get_stats():
	return json.dumps(update())


def pretty():
	return json.dumps(update(False), indent=4, sort_keys=True)


def shutdown():
	for t in thread_map:
		thread_map[t].active = False


class StatHandler(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header("Content-Type", "application/json")
		self.end_headers()
		if "pretty" in self.path:
			content = pretty()
		else:
			content = get_stats()
		self.wfile.write(bytes(content, 'utf8'))
		return


if __name__ == "__main__":
	logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
	update_containers()
	try:
		log.info("start server")
		httpd = socketserver.TCPServer(("", PORT), StatHandler)
		httpd.serve_forever()
	except KeyboardInterrupt:
		log.info("shutdown requested")
		httpd.socket.close()
	except Exception as e:
		log.exception(e)
	log.info("initiate shutdown")
	shutdown()
	log.info("wait for threads...")
