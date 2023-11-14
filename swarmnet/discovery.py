import subprocess
from swarmnet.logger import Logger
from typing import List

"""
If on adhoc network every device will be swarm member so just need to find which hosts are up
"""

base_ip = "192.168.0."
logger = Logger("discovery")

# def _discover_devices() -> [str]:
#   logger.info("Searching for all connected devices")
    
#   nearby_devices = []
#   for ping in range(1,256):
#     addr = base_ip + str(ping)
#     res = subprocess.call(['ping', '-c', '3', addr])
#     if(res == 0):
#       nearby_devices.append(addr)
  
#   n_devices = len(nearby_devices)
#   if n_devices == 1:
#     logger.info(f"Found 1 device connected")
#   elif n_devices > 1:
#     logger.info(f"Found {n_devices} devices connected")
#   else:
#     logger.warn(f"Found 0 devices connected")

#   for addr in nearby_devices:
#     logger.info(f"{addr}")
    
#   return nearby_devices
    
def discover_swarm_devices() -> List[str]:
  logger.info("Searching for all connected devices")
    
  nearby_devices = []
  for ping in range(2,255):
    addr = base_ip + str(ping)
    res = subprocess.call(['ping', '-c', '3', addr])
    if(res == 0):
      nearby_devices.append(addr)
  
  n_devices = len(nearby_devices)
  if n_devices == 1:
    logger.info(f"Found 1 device connected")
  elif n_devices > 1:
    logger.info(f"Found {n_devices} devices connected")
  else:
    logger.warn(f"Found 0 devices connected")

  for addr in nearby_devices:
    logger.info(f"{addr}")
    
  return nearby_devices