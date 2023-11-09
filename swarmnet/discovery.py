import bluetooth
from swarmnet.logger import Logger

def spawn_wifi_ap() -> None:
  logger = Logger("discovery")
  logger.info_header("Searching for nearby bluetooth devices")
  
  nearby_devices = bluetooth.discover_devices(lookup_names=True)
  logger.success("Found {} devices.".format(len(nearby_devices)))

  for addr, name in nearby_devices:
    logger.info("{} - {}".format(addr, name))