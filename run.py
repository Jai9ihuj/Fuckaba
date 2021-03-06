#!/usr/bin/python3

import sys
import subprocess
import socket

with socket.socket() as s:
	s.bind((sys.argv[1], int(sys.argv[2])))
	s.listen(255)

	process = subprocess.Popen(sys.argv[3: ], stdin = subprocess.PIPE, stdout = subprocess.PIPE)

	while True:
		command = process.stdout.read(1)[0]
		result = b"\x01"

		if command == 0:
			try:
				connection = s.accept()[0]

				result = b"\x00"
			except (NameError, OSError):
				pass
		elif command == 1:
			length = process.stdout.read(1)[0]

			try:
				received = connection.recv(length)

				result = b"\x00" + bytes([len(received)]) + received
			except (NameError, OSError):
				pass
		elif command == 2:
			length = process.stdout.read(1)[0]
			data = process.stdout.read(length)

			try:
				result = b"\x00" + bytes([connection.send(data)])
			except (NameError, OSError):
				pass
		elif command == 3:
			try:
				connection.close()

				result = b"\x00"
			except (NameError, OSError):
				pass

		process.stdin.write(result)
		process.stdin.flush()
