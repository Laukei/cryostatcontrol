import json
import logging 

import zmq

from .server import DEFAULT_PORT
from .handler import CommandHandler

DEFAULT_TIMEOUT = 5000
DEFAULT_IP = 'localhost'
logging.getLogger(__name__).addHandler(logging.NullHandler())

class BaseCommandSender:
	'''
	Low level command receiver that binds to IP/port and polls for incoming connections
	when get_events() is called.

	Takes kwargs:
		ip_address - IP address to bind to, default DEFAULT_IP
		port - port to bind to, default DEFAULT_PORT
		timeout - timeout in milliseconds to wait for response from server
	'''
	def __init__(self,**kwargs):
		self.ip_address = kwargs.get("ip_address",DEFAULT_IP)
		self.port = kwargs.get("port",DEFAULT_PORT)
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REQ)
		self.socket.setsockopt(zmq.LINGER,0)
		self.socket.RCVTIMEO = kwargs.get("timeout",DEFAULT_TIMEOUT)
		self.socket.connect("tcp://{}:{}".format(self.ip_address,self.port))
		logging.info('created socket connection')

	def _ask(self,req):
		self.socket.send_string(req)
		logging.debug('sent string {}'.format(req))
		self.message = self.socket.recv()
		logging.info('received string {}'.format(self.message))
		return self.message



class CommandSender(BaseCommandSender):
	'''
	Command sender that inherits BaseCommandSender. Creates a command handler or takes
	one as as kwarg.

	Takes kwargs:
		ip_address - IP address to bind to, default DEFAULT_IP
		port - port to bind to, default DEFAULT_PORT
		timeout - timeout in milliseconds to wait for response from server
		command_handler - preconfigured CommandHandler instance
		force - causes CommandSender to raise exception if server returns an error
	'''
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.ch = kwargs.get('command_handler',CommandHandler())
		self.force_handling = kwargs.get('force',False)
		self.no_reply = False


	def register_command(self,command,function):
		'''
		pass-through function for CommandHandler.
		'''
		self.ch.register_command(command,function)


	def _ask(self,req):
		'''
		Sends string to CommandReceiver, returning parsed json if successful
		or False if failure.
		'''
		try:
			super()._ask(req)
			return json.loads(self.message.decode('utf-8'))
		except zmq.error.Again as e:
			logging.exception('Sending to server timed out'.format())
			self.no_reply = True
		except zmq.error.ZMQError as e:
			logging.exception('Reply from server timed out'.format())
			self.no_reply = True
		return False


	def handle(self,command,*args,**kwargs):
		'''
		Performs command remotely, sending args and kwargs. If command is in
		local CommandHandler then CommandSender will try locally if fail remotely.
		If force handling is True and server returns an error, handle() will raise
		an exception rather than continuing.
		'''
		# if server working, send command
		if self.no_reply != True:
			req = self._make_request(command,args,kwargs)
			reply = self._ask(req)
			if reply != False:
				try:
					assert reply.get('error') == None
				except (AssertionError,AttributeError) as e:
					if self.force_handling == False:
						logging.warning('Error in response from server: {}'.format(reply))
					else:
						logging.exception('Error in response from server: {}'.format(reply))
						raise e
				return reply
		# else perform command locally
		# if command is registered with CommandHandler, perform it directly (locally) - 
		# useful if you're using this on a single machine
		try:
			assert self.ch.is_registered(command)
			reply = self.ch.handle(command,args,kwargs)
			return reply
		except AssertionError as e:
			logging.info('Unregistered command {} was skipped for local running'.format(command))
		return False


	def _make_request(self,command,args,kwargs):
		'''
		Takes handle() input and forms it into json package for ask()
		'''
		return json.dumps({'command':command,'args':args,'kwargs':kwargs})


def test():
	import time
	cs = CommandSender(force=False)
	cs.register_command('TEST',print)

	i = 0
	for request in range(10):
		i+=1
		message = cs.handle('TESTY',"Here are my parameters:","parameter")
		print("Received reply {}".format(message))
		time.sleep(0.1)


if __name__ == "__main__":
	test()