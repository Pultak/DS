import threading
import logging

import socket
import time


class BroadcastSignalerThread(threading.Thread):
	def __init__(self, ping_period, actual_node):
		threading.Thread.__init__(self)
		self.ping_period = ping_period
		self.running = True
		self.actual_node = actual_node

	# helper function to execute the threads
	def run(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

		# Enable broadcasting mode
		server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		# Set a timeout so the socket does not block
		# indefinitely when trying to receive data.
		server.settimeout(0.2)
		while self.running:
			logging.info('Sending broadcast ping!')
			self.actual_node.time = time.time()
			server.sendto(self.actual_node.to_string(), ("localhost", 37020))
			time.sleep(self.ping_period)


