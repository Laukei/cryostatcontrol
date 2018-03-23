from controller import TemperatureController
import logging
from logging.config import dictConfig
from config import log_config

dictConfig(log_config)
logger = logging.getLogger()

def main():
	tc = TemperatureController()
	tc.stage = 4
	tc.run()


if __name__ == '__main__':
	main()
