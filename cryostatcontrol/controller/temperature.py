import logging
import time

from legacy.Diode_Conversions import FDiodeConverter, DiodeConverter, RuO2Converter
from legacy.luke import lukes_staging_model, lukes_temperature_model
from hardware import PowerSupply, Model224, SIM900
from communicator import CommandReceiver
from config import addressbook

logging.getLogger(__name__).addHandler(logging.NullHandler())

class TemperatureController:
	def __init__(self):
		self.initialise()


	def initialise(self):
		self.ph = PowerSupply(addressbook['power_supply_1']['addr'],addressbook['power_supply_1']['channels'])
		self.ps = PowerSupply(addressbook['power_supply_2']['addr'],addressbook['power_supply_2']['channels'])
		self.temp = Model224(addressbook['temperature_readout']['addr'])
		self.sim = SIM900(addressbook['sim900_1']['addr'])

		self.res_bridge_address = addressbook['sim900_1']['modules']['ac_bridge']
		#just for reference, this is horrible and needs to go ^^^
		
		self.ph.set_output_state(False)
		self.ps.set_output_state(False)
		self.get_temperatures()
		self._is_running(False)

		self.cr = CommandReceiver()
		self.cr.register_command('sim900_1_ask',self.sim.ask)
		self.cr.register_command('sim900_1_read',self.sim.read)
		self.cr.register_command('sim900_1_write',self.sim.write)

		self._LUKE_reset_stage()


	def get_temperatures(self):
		'''
		ripe for spinning out into a thread (#justsayin)
		'''
		self.temps = dict(
			time = time.time(),
			FB = round(FDiodeConverter(self.temp.get_voltage('C1')),2),
			FourPH = round(DiodeConverter(self.temp.get_voltage('C2')),1),
			ThreePH = round(DiodeConverter(self.temp.get_voltage('C3')),1),
			FourPS = round(DiodeConverter(self.temp.get_voltage('C4')),1),
			ThreePS = round(DiodeConverter(self.temp.get_voltage('C5')),1),
			ThreeKBaf = round(self.temp.get_voltage('D5'),2),
			He3Hd = round(RuO2Converter(float(self.sim.ask(self.res_bridge_address,'RVAL?'))), 3)
		)
		return self.temps


	def run(self):
		self._is_running(True)
		while self._is_running():
			self._check_temperatures()
			wait(5)
			for key, value in self.temps.items():
				logging.info('{}: {}'.format(key,value))
			logging.info('stage {}, timer is {}, running: {}'.format(self.stage,self.stage_timer,self._is_running()))


	def wait(self,t):
		start_time = time.time()
		while True:
			self.cr.handle_queue()
			time.sleep(0.2)
			if time.time()-start_time > t:
				return


	def _is_running(self,state=None):
		if state != None:
			self.is_running = state
		else:
			return self.is_running


	def _check_temperatures(self):
		'''
		compares temps with targets, adjusts ph/ps:
		1. gets current temperatures
		2. checks staging information to see what stage to be in
		3. checks temperature model to find where temps should be for stage
			and applies values to hardware
		'''
		self.get_temperatures()
		self._LUKE_check_staging_model()
		self._LUKE_check_temperature_model()
		

	def _LUKE_reset_stage(self):
		self.stage = 1
		self.stage_timer = None
		self._is_running(False)


	def _LUKE_go_to_next_stage(self):
		if self.stage < 6:
			self.stage += 1
			self.stage_timer = None
		else:
			self._LUKE_reset_stage()


	def _LUKE_check_staging_model(self):
		staging_model = lukes_staging_model(self.stage,self.stage_timer,self.temps)
		logging.debug(staging_model)
		if staging_model.get('stage_timer') != None:
			self.stage_timer = staging_model.get('stage_timer')
		if staging_model.get('increment_stage') == True:
			self._LUKE_go_to_next_stage()


	def _LUKE_check_temperature_model(self):
		temperature_model = lukes_temperature_model(self.stage,self.temps)
		logging.debug(temperature_model)
		self._LUKE_control_powersupply(temperature_model.get('ThreePH'),self.ph,2)
		self._LUKE_control_powersupply(temperature_model.get('FourPH'),self.ph,1)
		self._LUKE_control_powersupply(temperature_model.get('ThreePS'),self.ps,2)
		self._LUKE_control_powersupply(temperature_model.get('FourPS'),self.ps,1)


	def _LUKE_control_powersupply(self,state,powersupply,channel):
		if state == None:
			powersupply.set_output_state(False,channel)
		else:
			powersupply.set_output_state(True,channel,**state)
