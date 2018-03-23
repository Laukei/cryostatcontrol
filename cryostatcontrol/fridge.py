import logging
from logging.config import dictConfig
import controller
from config import addressbook, log_config

dictConfig(log_config)
logger = logging.getLogger()


# stages of cycle
CHARGE = 10      # boiling 3He and 4He
HE4COOL = 20     # boiling 3He, using 4He
HE3COOL = 30     # using 3He, 4He
WARMUP = 40      # all heaters and switches off


class Fridge:
	'''
	Should sit in an event loop of its own with child threads to
	stabilize temperature 
	'''
	def __init__(self):
		self.initialise()

	def initialise(self):
		try:
			self.tc = controller.TemperatureController()
			self.sim2 = Sim900(addressbook['sim900_2'])
		except:
			logger.exception('Failed to initialise device')
			raise

	def set_stage(self,stage):
		self.stage = stage

	def get_stage(self):
		return self.stage
