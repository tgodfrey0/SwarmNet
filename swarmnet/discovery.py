import bluetooth
from swarmnet.logger import Logger

logger = Logger("discovery")

def _discover_bt_devices() -> [(str, str)]:
  logger.info("Searching for all nearby bluetooth devices")
  
  nearby_devices = bluetooth.discover_devices(lookup_names = True, lookup_class = False)
  n_devices = len(nearby_devices)
  if n_devices == 1:
    logger.success(f"Found 1 device within range")
  elif n_devices > 1:
    logger.success(f"Found {n_devices} device within range")
  else:
    logger.warn(f"Found 0 devices within range")

  # for addr, name in nearby_devices:
  #   logger.info("{} - {}".format(addr, name))
    
  return nearby_devices
    
def discover_swarm_devices(swarm_prefix: str) -> {str, str}:
  logger.info_header("Searching for swarm members")
  
  all_devices: [(str, str)] = _discover_bt_devices()
  
  swarm_devices: {str, str} = {}
  prefix_length = len(swarm_prefix)
  
  for addr, name in all_devices:
    if name[:prefix_length] == swarm_prefix:
      swarm_devices[name] = addr
      logger.info(f"Found {name} at {addr}")
      
  n_swarm_devices = len(swarm_devices)
  if n_swarm_devices == 1:
    logger.success(f"Found 1 swarm member (swarm prefix: {swarm_prefix})")
  elif n_swarm_devices > 1:
    logger.success(f"Found {n_swarm_devices} swarm members (swarm prefix: {swarm_prefix})")
  else:
    logger.warn(f"Found 0 swarm members (swarm prefix: {swarm_prefix})")
    
  return swarm_devices