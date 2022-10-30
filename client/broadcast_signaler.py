# import the threading module
import threading
import time
import logging

import socket
import time
import json


class BroadcastSignaler(threading.Thread):
	def __init__(self, ping_period, message="discover:new"):
		threading.Thread.__init__(self)
		self.ping_period = ping_period
		self.running = True
		self.message = message

	# helper function to execute the threads
	def run(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

		# Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
		# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
		# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
		# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
		# Thanks to @stevenreddie
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

		# Enable broadcasting mode
		server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		# Set a timeout so the socket does not block
		# indefinitely when trying to receive data.
		server.settimeout(0.2)
		while self.running:
			logging.info('Sending broadcast ping!')
			server.sendto(self.message, ("localhost", 37020))
			time.sleep(self.ping_period)


