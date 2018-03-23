import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

class CommandHandler:
	def __init__(self):
		self.handlers = {}

	def register_command(self,command,function):
		'''
		allows registering handlers for commands. Takes input

		command - string identifier for function
		function - the function to be executed

		No information about args or kwargs is included here.
		'''
		self.handlers[command] = function


	def handle(self,command,args,kwargs):
		'''
		Looks up function and runs it, returning reply 
		'''
		reply = self.handlers[command](*args,**kwargs)
		return reply


	def is_registered(self,command):
		if self.handlers.get(command):
			return True
		else:
			return False