from .instrument import GenericInstrument

class Model224(GenericInstrument):
	def __init__(self,address):
		super().__init__(address)
		self.handle.read_termination = '\r\n'


	def get_voltage(self,channel):
		return float(self.handle.ask('SRDG? {}[]'.format(channel))[:-1])
