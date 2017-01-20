import socket
import json
import threading
import time
import logging
from flask import Flask

log = logging.getLogger(__name__)
app = Flask(__name__)

containers = {}
thread_map = {}

class StatThread(threading.Thread):
	def __init__(self, container):
		threading.Thread.__init__(self)
		self.id = container
		self.active = True
	
	def run(self):
		with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
			sock.connect("/var/run/docker.sock")
			sock.send(bytes("GET /containers/{id}/stats HTTP/1.0\r\n\n".format(id=self.id),'utf8'))
			sock.settimeout(5)
			while(self.active):
				try:
					raw = sock.recv(16048) #TODO: basic containers have around 2000 bytes
					http = raw.decode('utf8')
					content = http.split("\n")[-2]
					log.info(len(content))
					if len(content) > 1:
						data = json.loads(content)
						log.info("{}: {}".format(self.id[0:12], len(data)))
						containers[self.id]["stats"] = data['read']
				except socket.timeout:
					log.error("container {} timed out".format(self.id[0:12]))
					self.active = False



def iterate_containers():
	containers = {}
	with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
		c.connect("/var/run/docker.sock")
		c.send(bytes("GET /containers/json HTTP/1.0\r\n\n",'ascii'))
		raw = c.recv(102400) #TODO: sufficient for roughly 128 containers
		log.info("container list length: %s", len(raw))

		http = raw.decode('utf8')
		data = json.loads(http.split("\n")[-2])

		for meta in data:
			containers[meta["Id"]] = {
				"name": meta["Names"][0],
				"id": meta["Id"],
				"state": meta["State"],
				"status": meta["Status"],
				"stats": {}
			}
	return containers

def manage_stat_threads():
	global containers
	stalled = []
	for t in thread_map:
		if t not in containers:
			thread_map[t].active = False
		if not thread_map[t].active:
			stalled.append(t)
	log.debug("stalled: "+str(stalled))
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
	manage_stat_threads()

@app.route("/")
def get_stats():
	update_containers()
	data = dict(containers)
	for c in data:
		if not c in thread_map or not thread_map[c].active:
			containers.pop(c)
	return json.dumps(data,indent=4)

def shutdown():
	for t in thread_map:
		thread_map[t].active=False

if __name__ == "__main__":
	logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
	update_containers()
	app.run()
	shutdown()

