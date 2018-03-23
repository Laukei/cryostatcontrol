import json
import logging 

import zmq

from .handler import CommandHandler


DEFAULT_IP = "*"
DEFAULT_PORT = 1550
logging.getLogger(__name__).addHandler(logging.NullHandler())


class BaseCommandReceiver:
	'''
	Low level command receiver that binds to IP/port and polls for incoming connections
	when get_events() is called.

	Takes kwargs:
		ip_address - IP address to bind to, default DEFAULT_IP
		port - port to bind to, default DEFAULT_PORT
	'''
	def __init__(self,**kwargs):
		self.ip_address = kwargs.get("ip_address",DEFAULT_IP)
		self.port = kwargs.get("port",DEFAULT_PORT)
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.REP)
		self.socket.bind("tcp://{}:{}".format(self.ip_address,self.port))
		self.poller = zmq.Poller()
		self.poller.register(self.socket, zmq.POLLIN)
		logging.info('created socket binding')

	def _get_events(self):
		self.evts = self.poller.poll(0)
		return self.evts


class CommandReceiver(BaseCommandReceiver):
	'''
	Command receiver that inherits BaseCommandReceiver. Creates a command handler or takes
	one as as kwarg.

	Takes kwargs:
		ip_address - IP address to bind to, default DEFAULT_IP
		port - port to bind to, default DEFAULT_PORT
		command_handler - preconfigured CommandHandler instance
		force - causes CommandReceiver to raise exception if command not in CommandHandler
	'''
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.ch = kwargs.get('command_handler',CommandHandler())
		self.force_handling = kwargs.get('force',False)


	def register_command(self,command,function):
		'''
		pass-through function for CommandHandler.
		'''
		self.ch.register_command(command,function)


	def _get_events(self):
		'''
		Used internally to poll for events and convert back to 
		CommandHandler format.
		'''
		super()._get_events()
		self.list_of_commands = []
		self.list_of_inputs = []
		for evt in self.evts:
			skt = evt[0]
			message = skt.recv(zmq.DONTWAIT)
			command = json.loads(message.decode('utf-8'))
			self.list_of_commands.append(command)
			self.list_of_inputs.append(skt)
		return self.list_of_commands


	def _send_responses(self,responses):
		'''
		Used internally to reply to events.
		'''
		assert len(responses) == len(self.list_of_inputs)
		for data in zip(self.list_of_inputs,responses):
			message = json.dumps(data[1])
			data[0].send_string(message)


	def handle_queue(self):
		'''
		Handles queue from _get_events using CommandHandler;
		call whenever you want the CommandReceiver to process its queue.
		'''
		self._get_events()
		self.responses = []
		for item in self.list_of_commands:
			try:
				assert self.ch.is_registered(item.get('command'))
				response = self.ch.handle(item.get('command'),item.get('args',[]),item.get('kwargs',{}))
				self.responses.append({'response':response})
			except AssertionError as e:
				if self.force_handling == False:
					logging.warning('Unregistered command submitted: {}'.format(item))
					self.responses.append({'error':'UNREGISTERED_COMMAND'})
				else:
					logging.exception('Unregistered command submitted: {}'.format(item))
					raise e
		self._send_responses(self.responses)


def test():
	import time
	cr = CommandReceiver()
	cr.register_command('TEST',print)

	i = 0
	while True:
		i+=1
		print("on cycle {}".format(i))
		cr.handle_queue()
		time.sleep(1)



if __name__ == "__main__":
	test()