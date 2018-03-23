from .instrument import GenericInstrument

class PowerSupply(GenericInstrument):
	def __init__(self,address,number_of_channels):
		super().__init__(address)
		self.number_of_channels = number_of_channels
		self.valid_channels = range(1,self.number_of_channels+1)
		self.current_channel = None
		self.channel_state = {i:None for i in self.valid_channels}


	def initialise(self):
		super().initialise()


	def set_output_state(self,state,channels=None,**kwargs):
		'''
		sets the output state of PowerSupply:

		set_output_state(False) turns off all channels

		set_output_state(True,2) turns on channel 2

		set_output_state(True,voltage=5,current=20) turns on
		    all channels and sets the output to 5 volts, 20mA
		'''
		channels = self._get_channels(channels)
		set_state = 'OFF' if state == False else 'ON'
		for c in channels:
			if (state == False and self.channel_state[c] == False) or (state == True and kwargs == self.channel_state[c]):
				continue
			else:
				self._select_channel(c)
				self.handle.write('CHAN:OUTP {}'.format(set_state))
				self.channel_state[c] = False if state == False else kwargs
				if 'voltage' in kwargs and 'current' in kwargs:
					self.handle.write('APPLY CH{}, {}V, {}mA'.format(c,
						kwargs.get('voltage'),
						kwargs.get('current')))
				elif 'voltage' in kwargs and 'current' not in kwargs:
					self.handle.write('VOLT {}V'.format(kwargs.get('voltage')))


	def _get_channels(self,channels):
		if channels == None:
			channels = self.valid_channels
		elif type(channels) == int:
			channels = (channels,)
		return channels


	def _select_channel(self,channel):
		assert channel in self.valid_channels
		if self.current_channel != channel:
			self.handle.write('INST:SEL CH{}'.format(channel))
			self.current_channel = channel
