#
#  Implementation of (horrible but functional) staging model from [Rankinator_Repeater.py by Luke Baker]
#
#  by Rob Heath
#
import time

def lukes_staging_model(stage,stage_timer,temps):
	'''
	looks at current stage and temps + time, recommends stage change
	'''
	FB = temps.get('FB')
	ThreePH = temps.get('ThreePH')
	FourPH = temps.get('FourPH')
	FourPS = temps.get('FourPS')
	ThreePS = temps.get('ThreePS')
	ThreeKBaf = temps.get('ThreeKBaf')
	He3Hd = temps.get('He3Hd')

	response = {}

	if stage == 1:
		if stage_timer == None:
			if FourPH > 40 and ThreePH > 40:
				response['stage_timer'] = time.time()
		elif time.time() - stage_timer > 20*60:
				response['increment_stage'] = True

	elif stage == 2:
		if stage_timer == None:
			response['stage_timer'] = time.time()
		elif time.time() - stage_timer > 30*60 or FB < 2.1:
			response['increment_stage'] = True

	elif stage == 3:
		if stage_timer == None:
			response['stage_timer'] = time.time()
		elif time.time() - stage_timer > 5*60 or He3Hd < 1.03:
			response['increment_stage'] = True

	elif stage == 4:
		if stage_timer == None:
			response['stage_timer'] = time.time()
		elif time.time() - stage_timer > 20*60 or He3Hd < 0.6:
			response['increment_stage'] = True

	elif stage == 5:
		if He3Hd > 0.65:
			response['increment_stage'] = True

	return response



def lukes_temperature_model(stage,temps):
	'''
	Implements the thermal control model from Rankinator_Repeater;
	takes stage and current temperatures, returns a dict where
	value = None means "turn off", otherwise supplies dict of
	voltage (and sometimes current) to be applied to heater at
	sensor. *Does not consider timings.*
	'''
	FB = temps.get('FB')
	ThreePH = temps.get('ThreePH')
	FourPH = temps.get('FourPH')
	FourPS = temps.get('FourPS')
	ThreePS = temps.get('ThreePS')
	ThreeKBaf = temps.get('ThreeKBaf')
	He3Hd = temps.get('He3Hd')

	response = {}

	if stage == 1:
		if ThreePH > 40.3:
			response['ThreePH'] = None
		elif ThreePH < 39:
			response['ThreePH'] = dict(voltage=30,current=40)
		else:
			response['ThreePH'] = dict(voltage=30,current=11)

		if FourPH > 40.2:
			response['FourPH'] = None
		elif FourPH < 39:
			response['FourPH'] = dict(voltage=30,current=60)
		else:
			response['FourPH'] = dict(voltage=30,current=9)

	elif stage == 2:
		if ThreePH > 44:
			response['ThreePH'] = None
		elif ThreePH < 43:
			response['ThreePH'] = dict(voltage=30,current=40)
		else:
			response['ThreePH'] = dict(voltage=30,current=10)

		if ThreePH > 45 or ThreePS > 10 or FB > 9 or ThreeKBaf > 9:
			response['FourPS'] = None
		elif ThreePS < 9 or FourPH < 25:
			if FourPS < 19:
				response['FourPS'] = dict(voltage=5.2)
			elif FourPS >= 19 and FourPS < 19.5:
				response['FourPS'] = dict(voltage=5)
			else:
				response['FourPS'] = dict(voltage=4.7)

	elif stage == 3:
		if ThreePH > 44:
			response['ThreePH'] = None
		elif ThreePH < 43:
			response['ThreePH'] = dict(voltage=30,current=40)
		else:
			response['ThreePH'] = dict(voltage=30,current=10)

		if FourPS < 19:
			response['FourPS'] = dict(voltage=5.2)
		elif FourPS >= 19 and FourPS < 19.5:
			response['FourPS'] = dict(voltage=5)
		else:
			response['FourPS'] = dict(voltage=4.7)

	elif stage == 4:
		if ThreePS < 16:
			response['ThreePS'] = dict(voltage=4.8)
		elif ThreePS >= 16 and ThreePS < 16.5:
			response['ThreePS'] = dict(voltage=4.5)
		else:
			response['ThreePS'] = dict(voltage=4.3)

		if FourPS < 19:
			response['FourPS'] = dict(voltage=5.2)
		elif FourPS >= 19 and FourPS < 19.5:
			response['FourPS'] = dict(voltage=5)
		else:
			response['FourPS'] = dict(voltage=4.7)

	elif stage == 5:
		if ThreePS < 16:
			response['ThreePS'] = dict(voltage=4.8)
		elif ThreePS >= 16 and ThreePS < 16.5:
			response['ThreePS'] = dict(voltage=4.5)
		else:
			response['ThreePS'] = dict(voltage=4.3)

		if FourPS < 19:
			response['FourPS'] = dict(voltage=5.2)
		elif FourPS >= 19 and FourPS < 19.5:
			response['FourPS'] = dict(voltage=5)
		else:
			response['FourPS'] = dict(voltage=4.7)

	return response
