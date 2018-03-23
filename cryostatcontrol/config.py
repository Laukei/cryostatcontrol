#from fridge import CHARGE, HE4COOL, HE3COOL, WARMUP

addressbook = {
	'power_supply_1':{'addr':'GPIB0::3','channels':3}, #KeithPH_port 
	'power_supply_2':{'addr':'GPIB0::4','channels':3}, #KeithPS_port
	'temperature_readout':{'addr':'GPIB0::12'}, #Model_224_port
	'sim900_1':{'addr':'GPIB0::2','modules':{'ac_bridge':1}}, #SIM900_port
	'sim900_2':{'addr':'ASRL1'} #SIM9002_port
}


log_config = dict(
	version = 1,
	formatters = {
		'f' : {'format':'%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
	},
	handlers = {
		'h': {'class': 'logging.StreamHandler',
			'formatter': 'f',
			'level': 'DEBUG'},
		'g': {'class': 'logging.FileHandler',
                        'filename': 'log.txt',
                        'mode': 'w',
			'formatter': 'f',
			'level': 'DEBUG'}
		},
	root = {
		'handlers': ['h','g'],
		'level': 'DEBUG'
	},
)
